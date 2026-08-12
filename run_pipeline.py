#!/usr/bin/env python3
"""Run the City of North Vancouver GIS analysis pipeline.

    python run_pipeline.py --all        download, process, map and report
    python run_pipeline.py --download   acquisition and validation only
    python run_pipeline.py --process    boundary through spatial joins and analysis
    python run_pipeline.py --maps       static maps and the interactive map
    python run_pipeline.py --report     QA tests and the final report

Stages run in order and the run stops at the first failure, so a broken stage never
silently feeds bad data downstream.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SCRIPTS = ROOT / "scripts"
PYTHON = sys.executable

STAGES = {
    "download": [
        ("01_download.py", "Download every configured source into data/raw/"),
        ("02_validate_sources.py", "Hash-verify and validate every raw file"),
    ],
    "process": [
        ("03_prepare_boundary.py", "Municipal boundary and neighbourhoods"),
        ("04_prepare_census.py", "2021 Census dissemination areas"),
        ("05_prepare_housing.py", "Dwelling structure, zoning and land use"),
        ("06_prepare_buildings.py", "Building footprints and classification"),
        ("07_prepare_elections.py", "Election results and voting places"),
        ("08_prepare_roads.py", "Street network and derived intersections"),
        ("09_prepare_traffic.py", "Signals, volumes and signs"),
        ("10_prepare_transit.py", "TransLink GTFS stops, routes and frequency"),
        ("11_prepare_parking.py", "Parking supply, occupancy and restrictions"),
        ("12_prepare_safety.py", "ICBC collisions matched to intersections"),
        ("13_spatial_joins.py", "Master intersection table"),
        ("14_analysis_population.py", "Population and neighbourhood analysis"),
        ("15_analysis_housing.py", "Housing rankings"),
        ("16_analysis_polling.py", "Voting places in population context"),
        ("17_analysis_intersections.py", "Neutral public-space scoring"),
    ],
    "maps": [
        ("18_create_maps.py", "Static map series"),
        ("19_create_interactive_map.py", "Interactive web map"),
        ("22_campaign_visibility.py", "Public visibility recommendations"),
        ("23_create_qgis_project.py", "QGIS desktop project"),
    ],
    "report": [
        ("20_generate_report.py", "Final HTML report and DATA_SOURCES.md"),
    ],
}

ORDER = ["download", "process", "maps", "report"]


def run(script: str, description: str, extra: list[str]) -> tuple[bool, float]:
    path = SCRIPTS / script
    print(f"\n\033[1m▶ {script}\033[0m — {description}", flush=True)
    print("─" * 78, flush=True)
    start = time.time()
    result = subprocess.run([PYTHON, str(path), *extra], cwd=ROOT)
    elapsed = time.time() - start
    ok = result.returncode == 0
    print(f"{'✓' if ok else '✗'} {script} finished in {elapsed:.1f}s "
          f"(exit {result.returncode})", flush=True)
    return ok, elapsed


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--all", action="store_true", help="run every stage")
    ap.add_argument("--download", action="store_true")
    ap.add_argument("--process", action="store_true")
    ap.add_argument("--maps", action="store_true")
    ap.add_argument("--report", action="store_true")
    ap.add_argument("--force", action="store_true",
                    help="re-download raw files that already exist")
    ap.add_argument("--skip-tests", action="store_true",
                    help="do not run pytest before the report stage")
    args = ap.parse_args()

    selected = [s for s in ORDER if getattr(args, s)] or (ORDER if args.all else [])
    if not selected:
        ap.print_help()
        return 1

    print("\033[1mCity of North Vancouver — GIS analysis pipeline\033[0m")
    print(f"stages: {', '.join(selected)}")

    results, total = [], 0.0
    for stage in selected:
        print(f"\n\033[1m═══ {stage.upper()} ═══\033[0m")
        for script, desc in STAGES[stage]:
            extra = ["--force"] if (args.force and script == "01_download.py") else []
            ok, elapsed = run(script, desc, extra)
            results.append((script, ok, elapsed))
            total += elapsed
            if not ok:
                print(f"\n\033[31mPipeline stopped: {script} failed.\033[0m")
                print("Nothing downstream was run, so no stale output was produced.")
                return 1

        if stage == "report" and not args.skip_tests:
            pass  # tests run before the report below

    # QA runs before the report is considered trustworthy.
    if "report" in selected and not args.skip_tests:
        print("\n\033[1m▶ pytest\033[0m — automated quality assurance")
        print("─" * 78, flush=True)
        qa = subprocess.run([PYTHON, "-m", "pytest", "tests/", "-q"], cwd=ROOT)
        if qa.returncode != 0:
            print("\n\033[31mQA tests failed. The report may not be trustworthy.\033[0m")
            return 1
        print("✓ QA passed")

    print("\n" + "═" * 78)
    print(f"\033[1mPipeline complete\033[0m — {len(results)} stages in {total:.1f}s")
    print("═" * 78)
    for script, ok, elapsed in results:
        print(f"  {'✓' if ok else '✗'} {script:<34} {elapsed:6.1f}s")
    print("\nOutputs:")
    print("  data/processed/      GeoPackages")
    print("  outputs/maps/        static maps")
    print("  outputs/interactive/ interactive map (python -m http.server --directory .)")
    print("  outputs/tables/      CSV rankings and inventories")
    print("  outputs/report/      final report")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
