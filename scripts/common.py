"""Shared helpers for the CNV GIS pipeline.

Kept deliberately small: path resolution, config loading, logging and the
raw-data metadata sidecar format that every downloader writes.
"""
from __future__ import annotations

import hashlib
import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CONFIG_DIR = PROJECT_ROOT / "config"
DATA_RAW = PROJECT_ROOT / "data" / "raw"
DATA_INTERIM = PROJECT_ROOT / "data" / "interim"
DATA_PROCESSED = PROJECT_ROOT / "data" / "processed"
OUTPUTS = PROJECT_ROOT / "outputs"
LOGS = PROJECT_ROOT / "logs"


def get_logger(name: str) -> logging.Logger:
    LOGS.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger
    logger.setLevel(logging.INFO)
    fmt = logging.Formatter("%(asctime)s %(levelname)-7s %(name)s: %(message)s", "%H:%M:%S")

    stream = logging.StreamHandler(sys.stdout)
    stream.setFormatter(fmt)
    logger.addHandler(stream)

    fh = logging.FileHandler(LOGS / f"{name}.log", encoding="utf-8")
    fh.setFormatter(fmt)
    logger.addHandler(fh)
    return logger


def load_yaml(path: Path) -> dict:
    with open(path, encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def load_sources() -> dict:
    return load_yaml(CONFIG_DIR / "sources.yaml")


def load_study_area() -> dict:
    return load_yaml(CONFIG_DIR / "study_area.yaml")


def sha256_file(path: Path, chunk: int = 1 << 20) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        while block := fh.read(chunk):
            h.update(block)
    return h.hexdigest()


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def write_metadata(target: Path, meta: dict) -> Path:
    """Write the .meta.json sidecar that accompanies every raw download."""
    meta_path = target.with_suffix(target.suffix + ".meta.json")
    meta_path.write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")
    return meta_path


def read_metadata(target: Path) -> dict | None:
    meta_path = target.with_suffix(target.suffix + ".meta.json")
    if not meta_path.exists():
        return None
    try:
        return json.loads(meta_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None


# --- content validation -----------------------------------------------------

MAGIC = {
    "zip": (b"PK\x03\x04", b"PK\x05\x06"),
    "pdf": (b"%PDF",),
}

_HTML_MARKERS = (b"<!doctype html", b"<html", b"<head", b"<body", b"<!DOCTYPE HTML")


def looks_like_html(head: bytes) -> bool:
    lowered = head[:2048].lower()
    return any(m.lower() in lowered for m in _HTML_MARKERS)


def validate_magic(path: Path, expect: str | None) -> tuple[bool, str]:
    """Guard against HTML error pages saved under a .zip/.pdf name."""
    with open(path, "rb") as fh:
        head = fh.read(4096)

    if not head:
        return False, "file is empty"

    if expect:
        wanted = MAGIC.get(expect)
        if wanted and not any(head.startswith(w) for w in wanted):
            if looks_like_html(head):
                return False, f"expected {expect} but received an HTML page (likely an error page)"
            return False, f"expected {expect} magic bytes, got {head[:8]!r}"
        return True, "ok"

    if looks_like_html(head):
        return True, "html content (expected)"
    return True, "ok"


# --- geospatial helpers -----------------------------------------------------

def load_boundary(layer: str = "cnv_boundary"):
    """Load a layer from the processed boundary GeoPackage."""
    import geopandas as gpd

    return gpd.read_file(DATA_PROCESSED / "cnv_boundary.gpkg", layer=layer)


def load_raw_vector(rel_path: str, analysis_crs: str = "EPSG:26910"):
    """Read a raw GeoJSON pulled from the CNV ArcGIS server into the analysis CRS.

    The server emits EPSG:26910 but some layers omit a usable CRS declaration, so it is
    asserted rather than assumed absent.
    """
    import geopandas as gpd

    gdf = gpd.read_file(DATA_RAW / rel_path)
    if gdf.crs is None:
        gdf = gdf.set_crs(analysis_crs)
    gdf = gdf.to_crs(analysis_crs)
    if len(gdf):
        gdf["geometry"] = gdf.geometry.make_valid()
    return gdf


def clip_to_cnv(gdf, boundary=None, how: str = "clip"):
    """Restrict a layer to the CNV municipal boundary.

    how='clip'      cuts geometries at the boundary (for lines/polygons)
    how='within'    keeps whole features whose representative point is inside (for points)
    """
    import geopandas as gpd

    if boundary is None:
        boundary = load_boundary()
    boundary = boundary.to_crs(gdf.crs)

    if how == "within":
        pts = gdf.copy()
        pts["geometry"] = gdf.geometry.representative_point()
        hit = gpd.sjoin(pts, boundary[["geometry"]], predicate="within", how="inner")
        return gdf.loc[gdf.index.isin(hit.index)].copy()
    return gpd.clip(gdf, boundary)


def tag_source(gdf, source: str, url: str, license_: str = "City of North Vancouver open data terms"):
    """Attach the source metadata every processed layer must carry."""
    gdf = gdf.copy()
    gdf["source"] = source
    gdf["source_url"] = url
    gdf["license"] = license_
    gdf["prepared_utc"] = utc_now()
    return gdf
