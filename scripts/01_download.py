#!/usr/bin/env python3
"""Download every source defined in config/sources.yaml into data/raw/.

Rules enforced here (see PROJECT_BRIEF section 5):
  * raw files are never overwritten unless --force is given
  * every download gets a SHA256 and a .meta.json sidecar
  * failed downloads are retried with backoff and then logged, never faked
  * downloads are validated so an HTML error page can never masquerade as a zip

Usage:
    python scripts/01_download.py
    python scripts/01_download.py --force
    python scripts/01_download.py --only statcan_census_profile_bc_da
    python scripts/01_download.py --skip statcan_census_profile_bc_da
    python scripts/01_download.py --group statcan
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
import time
from pathlib import Path
from urllib.parse import urlencode

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import (  # noqa: E402
    DATA_RAW,
    OUTPUTS,
    get_logger,
    load_sources,
    read_metadata,
    sha256_file,
    utc_now,
    validate_magic,
    write_metadata,
)

log = get_logger("01_download")

USER_AGENT = (
    "CNV-GIS-Research/1.0 (municipal open-data analysis; contact: project maintainer)"
)


def session_with_retries(retries: int) -> requests.Session:
    s = requests.Session()
    s.headers.update({"User-Agent": USER_AGENT})
    return s


# ---------------------------------------------------------------------------
# handlers
# ---------------------------------------------------------------------------


def download_http_file(src: dict, target: Path, defaults: dict, sess: requests.Session) -> dict:
    url = src["download_url"]
    timeout = defaults.get("timeout_seconds", 180)
    tmp = target.with_suffix(target.suffix + ".part")

    with sess.get(url, stream=True, timeout=timeout, allow_redirects=True) as r:
        r.raise_for_status()
        total = int(r.headers.get("Content-Length") or 0)
        written = 0
        last_report = 0
        with open(tmp, "wb") as fh:
            for chunk in r.iter_content(chunk_size=1 << 20):
                if not chunk:
                    continue
                fh.write(chunk)
                written += len(chunk)
                if total and written - last_report > 50 * (1 << 20):
                    last_report = written
                    log.info("    %s: %.0f MB / %.0f MB", src["source_id"],
                             written / 1e6, total / 1e6)
        content_disposition = r.headers.get("Content-Disposition")
        content_type = r.headers.get("Content-Type")

    ok, reason = validate_magic(tmp, src.get("expect_magic"))
    if not ok:
        tmp.unlink(missing_ok=True)
        raise ValueError(f"content validation failed: {reason}")

    tmp.replace(target)
    return {
        "http_content_type": content_type,
        "http_content_disposition": content_disposition,
        "bytes": target.stat().st_size,
        "validation": reason,
    }


def fetch_by_oid(src, base_params, fetch, meta, page_size, log):
    """Retrieve a layer by OBJECTID ranges, bisecting around features the server cannot serve.

    Some CNV layers hold geometry that the ArcGIS service fails to serialise, returning a
    generic HTTP 400 for any page containing the offending record. Bisecting isolates those
    records so the rest of the layer is still usable, and reports exactly what was lost
    instead of silently returning a short layer.
    """
    oid_field = meta.get("objectIdField") or "OBJECTID"
    ids_resp = fetch({"where": "1=1", "returnIdsOnly": "true", "f": "json"})
    oids = sorted(ids_resp.get("objectIds") or [])

    collected: list[dict] = []
    unreadable: list[int] = []

    def grab(chunk: list[int]) -> None:
        if not chunk:
            return
        where = f"{oid_field} >= {chunk[0]} AND {oid_field} <= {chunk[-1]}"
        try:
            collected.extend(fetch(dict(base_params, where=where)).get("features", []))
            return
        except ValueError:
            if len(chunk) == 1:
                unreadable.append(chunk[0])
                log.warning("    %s: OBJECTID %d is unreadable on the server",
                            src["source_id"], chunk[0])
                return
        mid = len(chunk) // 2
        grab(chunk[:mid])
        grab(chunk[mid:])

    for i in range(0, len(oids), page_size):
        grab(oids[i : i + page_size])

    return collected, unreadable


def download_arcgis_layer(src: dict, target: Path, defaults: dict, sess: requests.Session) -> dict:
    """Page through an ArcGIS REST layer and assemble a single GeoJSON FeatureCollection.

    Uses resultOffset paging. Falls back to OBJECTID-range paging when the service
    reports that it does not support pagination.
    """
    servers = src["_servers"]
    base = f"{servers['cnv_arcgis']}/{src['service']}/{src['layer_id']}"
    timeout = defaults.get("timeout_seconds", 180)
    page_size = src.get("page_size") or defaults.get("arcgis_page_size", 1000)
    out_sr = defaults.get("arcgis_out_sr", 26910)

    meta = sess.get(f"{base}?f=json", timeout=timeout).json()
    if "error" in meta:
        raise ValueError(f"layer metadata error: {meta['error']}")
    supports_pagination = meta.get("advancedQueryCapabilities", {}).get(
        "supportsPagination", False
    )

    count_params = {"where": "1=1", "returnCountOnly": "true", "f": "json"}
    count_resp = sess.get(f"{base}/query?{urlencode(count_params)}", timeout=timeout).json()
    total = count_resp.get("count")

    features: list[dict] = []
    unreadable: list[int] = []
    crs_wkid = None

    def fetch(params: dict) -> dict:
        resp = sess.get(f"{base}/query?{urlencode(params)}", timeout=timeout)
        resp.raise_for_status()
        data = resp.json()
        if "error" in data:
            raise ValueError(f"query error: {data['error']}")
        return data

    base_params = {
        "where": "1=1",
        "outFields": "*",
        "returnGeometry": "true",
        "outSR": out_sr,
        "f": "geojson",
    }

    def fetch_page(offset: int, size: int) -> tuple[dict, int]:
        """Fetch one page, halving the page size when the service refuses the request.

        Layers with very complex geometry (e.g. road polygons) fail with a generic
        HTTP 400 above a certain response size, so back off rather than give up.
        """
        nonlocal page_size
        size = min(size, page_size)
        while True:
            try:
                return fetch(dict(base_params, resultOffset=offset, resultRecordCount=size)), size
            except ValueError:
                if size <= 25:
                    raise
                size = max(25, size // 2)
                page_size = size
                log.info("    %s: reducing page size to %d", src["source_id"], size)

    if supports_pagination and src.get("paging") != "oid":
        offset = 0
        while True:
            data, used = fetch_page(offset, page_size)
            batch = data.get("features", [])
            features.extend(batch)
            crs_wkid = crs_wkid or (data.get("crs") or {}).get("properties", {}).get("name")
            if len(batch) < used:
                break
            offset += len(batch)
            if total and offset >= total:
                break
    else:
        features, unreadable = fetch_by_oid(src, base_params, fetch, meta, page_size, log)

    fc = {
        "type": "FeatureCollection",
        "crs": {"type": "name", "properties": {"name": f"urn:ogc:def:crs:EPSG::{out_sr}"}},
        "features": features,
    }
    target.write_text(json.dumps(fc), encoding="utf-8")

    expected = src.get("expected_count")
    warn = None
    if total is not None and len(features) != total:
        warn = f"server reported {total} features, retrieved {len(features)}"
        log.warning("    %s: %s", src["source_id"], warn)
    if expected is not None and len(features) != expected:
        msg = f"expected_count {expected} in config, retrieved {len(features)}"
        log.warning("    %s: %s", src["source_id"], msg)
        warn = f"{warn}; {msg}" if warn else msg

    if unreadable:
        note = (f"{len(unreadable)} feature(s) could not be served by the ArcGIS endpoint "
                f"(OBJECTIDs {unreadable[:20]}{'...' if len(unreadable) > 20 else ''})")
        warn = f"{warn}; {note}" if warn else note

    return {
        "feature_count": len(features),
        "unreadable_objectids": unreadable,
        "server_reported_count": total,
        "layer_name": meta.get("name"),
        "geometry_type": meta.get("geometryType"),
        "supports_pagination": supports_pagination,
        "out_sr": out_sr,
        "bytes": target.stat().st_size,
        "warning": warn,
    }


def download_wfs(src: dict, target: Path, defaults: dict, sess: requests.Session) -> dict:
    servers = src["_servers"]
    params = {
        "service": "WFS",
        "version": "2.0.0",
        "request": "GetFeature",
        "typeName": src["typename"],
        "outputFormat": "application/json",
        "srsName": "EPSG:3005",
    }
    if src.get("cql_filter"):
        params["CQL_FILTER"] = src["cql_filter"]

    r = sess.get(servers["bc_wfs"], params=params, timeout=defaults.get("timeout_seconds", 180))
    r.raise_for_status()
    data = r.json()
    if "features" not in data:
        raise ValueError(f"WFS response contained no feature collection: {str(data)[:300]}")
    if not data["features"]:
        raise ValueError("WFS returned zero features - check CQL_FILTER")

    target.write_text(json.dumps(data), encoding="utf-8")
    return {
        "feature_count": len(data["features"]),
        "typename": src["typename"],
        "cql_filter": src.get("cql_filter"),
        "srs": "EPSG:3005",
        "bytes": target.stat().st_size,
    }


def download_html_page(src: dict, target: Path, defaults: dict, sess: requests.Session) -> dict:
    r = sess.get(src["url"], timeout=defaults.get("timeout_seconds", 180), allow_redirects=True)
    r.raise_for_status()
    target.write_bytes(r.content)
    return {
        "bytes": len(r.content),
        "http_content_type": r.headers.get("Content-Type"),
        "final_url": r.url,
    }


HANDLERS = {
    "http_file": download_http_file,
    "arcgis_layer": download_arcgis_layer,
    "wfs": download_wfs,
    "html_page": download_html_page,
}


# ---------------------------------------------------------------------------
# driver
# ---------------------------------------------------------------------------


def process_source(src: dict, defaults: dict, sess: requests.Session, force: bool) -> dict:
    sid = src["source_id"]
    target = DATA_RAW / src["out_dir"] / src["filename"]
    target.parent.mkdir(parents=True, exist_ok=True)

    row = {
        "source_id": sid,
        "organization": src.get("organization", ""),
        "dataset": src.get("dataset", ""),
        "url": src.get("url", ""),
        "download_url": src.get("download_url", src.get("url", "")),
        "format": src.get("format", ""),
        "geographic_level": src.get("geographic_level", ""),
        "coverage": src.get("coverage", ""),
        "version": src.get("version", ""),
        "license": src.get("license", ""),
        "download_date": "",
        "local_path": str(target.relative_to(DATA_RAW.parent.parent)),
        "status": "",
        "sha256": "",
        "bytes": "",
        "feature_count": "",
        "notes": (src.get("notes") or "").strip().replace("\n", " "),
    }

    if target.exists() and not force:
        existing = read_metadata(target) or {}
        row["status"] = "cached"
        row["download_date"] = existing.get("download_date", "")
        row["sha256"] = existing.get("sha256", "")
        row["bytes"] = existing.get("bytes", target.stat().st_size)
        row["feature_count"] = existing.get("feature_count", "")
        log.info("  [cached]  %s", sid)
        return row

    handler = HANDLERS[src["handler"]]
    retries = defaults.get("retries", 4)
    backoff = defaults.get("backoff_seconds", 3)

    last_err = None
    for attempt in range(1, retries + 1):
        try:
            log.info("  [get]     %s (attempt %d/%d)", sid, attempt, retries)
            detail = handler(src, target, defaults, sess)
            digest = sha256_file(target)

            meta = {
                "source_id": sid,
                "organization": src.get("organization"),
                "dataset": src.get("dataset"),
                "source_url": src.get("url"),
                "download_url": src.get("download_url", src.get("url")),
                "handler": src["handler"],
                "format": src.get("format"),
                "geographic_level": src.get("geographic_level"),
                "coverage": src.get("coverage"),
                "version": src.get("version"),
                "license": src.get("license"),
                "download_date": utc_now(),
                "sha256": digest,
                "notes": (src.get("notes") or "").strip(),
                **detail,
            }
            write_metadata(target, meta)

            row["status"] = "ok"
            row["download_date"] = meta["download_date"]
            row["sha256"] = digest
            row["bytes"] = detail.get("bytes", "")
            row["feature_count"] = detail.get("feature_count", "")
            log.info("  [ok]      %s  (%s bytes%s)", sid, row["bytes"],
                     f", {row['feature_count']} features" if row["feature_count"] != "" else "")
            return row
        except Exception as exc:  # noqa: BLE001 - we want to record any failure
            last_err = exc
            log.warning("  [retry]   %s: %s", sid, str(exc)[:200])
            if attempt < retries:
                time.sleep(backoff * attempt)

    row["status"] = "FAILED"
    row["notes"] = f"{row['notes']} | FAILURE: {str(last_err)[:300]}".strip(" |")
    log.error("  [FAILED]  %s: %s", sid, str(last_err)[:300])
    return row


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--force", action="store_true", help="re-download even if the raw file exists")
    ap.add_argument("--only", nargs="*", help="only these source_ids")
    ap.add_argument("--skip", nargs="*", default=[], help="skip these source_ids")
    ap.add_argument("--group", nargs="*", help="only sources whose out_dir matches")
    args = ap.parse_args()

    cfg = load_sources()
    defaults = cfg.get("defaults", {})
    servers = cfg.get("servers", {})
    sources = cfg["sources"]

    if args.only:
        sources = [s for s in sources if s["source_id"] in args.only]
    if args.group:
        sources = [s for s in sources if s["out_dir"] in args.group]
    if args.skip:
        sources = [s for s in sources if s["source_id"] not in args.skip]

    log.info("Downloading %d source(s) into %s", len(sources), DATA_RAW)
    sess = session_with_retries(defaults.get("retries", 4))

    rows = []
    for src in sources:
        src["_servers"] = servers
        rows.append(process_source(src, defaults, sess, args.force))

    OUTPUTS.joinpath("tables").mkdir(parents=True, exist_ok=True)
    inv = OUTPUTS / "tables" / "data_inventory.csv"

    # A partial run (--only/--group) must update the inventory rather than truncate it,
    # so the table always reflects every configured source.
    merged: dict[str, dict] = {}
    if inv.exists():
        with open(inv, newline="", encoding="utf-8") as fh:
            for old in csv.DictReader(fh):
                merged[old["source_id"]] = old
    for r in rows:
        merged[r["source_id"]] = r

    configured = [s["source_id"] for s in cfg["sources"]]
    ordered = [merged[sid] for sid in configured if sid in merged]

    with open(inv, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(ordered)

    ok = sum(r["status"] == "ok" for r in rows)
    cached = sum(r["status"] == "cached" for r in rows)
    failed = [r for r in rows if r["status"] == "FAILED"]

    log.info("-" * 70)
    log.info("downloaded=%d cached=%d failed=%d", ok, cached, len(failed))
    log.info("inventory written to %s", inv)
    for r in failed:
        log.error("FAILED %-38s %s", r["source_id"], r["notes"][:150])

    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
