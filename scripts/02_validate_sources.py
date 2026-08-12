#!/usr/bin/env python3
"""Validate everything in data/raw/ before any processing runs.

Checks per file: existence, non-zero size, SHA256 match against the sidecar,
container integrity (zip/PDF/CSV/GeoJSON), and for vector payloads that the
geometry parses and carries a CRS.

Writes outputs/tables/source_validation.csv. Exits non-zero if any source fails.
"""
from __future__ import annotations

import csv
import json
import sys
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import (  # noqa: E402
    DATA_RAW,
    OUTPUTS,
    PROJECT_ROOT,
    get_logger,
    load_sources,
    read_metadata,
    sha256_file,
)

log = get_logger("02_validate_sources")


def validate_zip(path: Path) -> tuple[str, str]:
    try:
        with zipfile.ZipFile(path) as z:
            bad = z.testzip()
            if bad:
                return "FAIL", f"corrupt member: {bad}"
            names = z.namelist()
        return "ok", f"{len(names)} members"
    except zipfile.BadZipFile as exc:
        return "FAIL", f"not a valid zip: {exc}"


def validate_geojson(path: Path) -> tuple[str, str]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return "FAIL", f"invalid JSON: {exc}"

    feats = data.get("features")
    if feats is None:
        return "FAIL", "no 'features' key"
    if not feats:
        return "WARN", "zero features"

    crs = (data.get("crs") or {}).get("properties", {}).get("name", "")
    geom_missing = sum(1 for f in feats if not f.get("geometry"))
    note = f"{len(feats)} features, crs={crs or 'UNDECLARED'}"
    if geom_missing:
        note += f", {geom_missing} without geometry"
    if not crs:
        return "WARN", note
    return "ok", note


def validate_pdf(path: Path) -> tuple[str, str]:
    head = path.open("rb").read(5)
    if not head.startswith(b"%PDF"):
        return "FAIL", "missing %PDF header"
    return "ok", f"{path.stat().st_size // 1024} KB"


def validate_csv(path: Path) -> tuple[str, str]:
    try:
        with open(path, encoding="utf-8-sig", newline="") as fh:
            reader = csv.reader(fh)
            header = next(reader, None)
            rows = sum(1 for _ in reader)
        if not header:
            return "FAIL", "empty CSV"
        return "ok", f"{rows} rows, {len(header)} cols"
    except UnicodeDecodeError as exc:
        return "FAIL", f"encoding error: {exc}"


def validate_html(path: Path) -> tuple[str, str]:
    text = path.read_text(encoding="utf-8", errors="replace")
    if "<html" not in text.lower():
        return "WARN", "does not look like HTML"
    return "ok", f"{len(text) // 1024} KB"


def main() -> int:
    cfg = load_sources()
    rows = []

    for src in cfg["sources"]:
        sid = src["source_id"]
        path = DATA_RAW / src["out_dir"] / src["filename"]
        row = {
            "source_id": sid,
            "local_path": str(path.relative_to(PROJECT_ROOT)),
            "exists": path.exists(),
            "bytes": path.stat().st_size if path.exists() else 0,
            "sha256_ok": "",
            "content_status": "",
            "detail": "",
        }

        if not path.exists():
            row["content_status"] = "MISSING"
            row["detail"] = "file not downloaded"
            rows.append(row)
            log.error("MISSING  %s", sid)
            continue

        meta = read_metadata(path)
        if meta and meta.get("sha256"):
            row["sha256_ok"] = sha256_file(path) == meta["sha256"]
            if not row["sha256_ok"]:
                log.error("HASH MISMATCH %s - raw file changed since download", sid)
        else:
            row["sha256_ok"] = "no-sidecar"

        suffix = path.suffix.lower()
        if suffix == ".zip":
            status, detail = validate_zip(path)
        elif suffix == ".geojson":
            status, detail = validate_geojson(path)
        elif suffix == ".pdf":
            status, detail = validate_pdf(path)
        elif suffix == ".csv":
            status, detail = validate_csv(path)
        elif suffix in (".html", ".htm"):
            status, detail = validate_html(path)
        else:
            status, detail = "ok", "no validator for this extension"

        # Surface any download-time warning (e.g. unreadable server features).
        if meta and meta.get("warning"):
            detail = f"{detail} | download warning: {meta['warning']}"
            if status == "ok":
                status = "WARN"

        row["content_status"] = status
        row["detail"] = detail
        rows.append(row)

        level = {"ok": log.info, "WARN": log.warning}.get(status, log.error)
        level("%-8s %-40s %s", status, sid, detail)

    OUTPUTS.joinpath("tables").mkdir(parents=True, exist_ok=True)
    out = OUTPUTS / "tables" / "source_validation.csv"
    with open(out, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    fails = [r for r in rows if r["content_status"] in ("FAIL", "MISSING")]
    warns = [r for r in rows if r["content_status"] == "WARN"]
    hash_bad = [r for r in rows if r["sha256_ok"] is False]

    log.info("-" * 70)
    log.info("validated=%d ok=%d warn=%d fail=%d hash_mismatch=%d",
             len(rows), len(rows) - len(fails) - len(warns), len(warns), len(fails), len(hash_bad))
    log.info("written to %s", out)
    return 1 if fails or hash_bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
