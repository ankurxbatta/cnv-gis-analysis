#!/usr/bin/env bash
# Run a script under QGIS's bundled Python so PyQGIS is importable.
#
# The macOS QGIS bundle ships python3.12 but no PYTHONHOME layout it can boot from,
# so a small shim directory is created with lib/python3.12 pointing at the bundled
# standard library. Usage:
#     ./scripts/run_qgis_python.sh scripts/23_create_qgis_project.py
set -euo pipefail

APP=$(ls -d /Applications/QGIS*.app 2>/dev/null | head -1)
[ -n "$APP" ] || { echo "QGIS not found in /Applications" >&2; exit 1; }

SHIM="${TMPDIR:-/tmp}/qgis_pyhome"
rm -rf "$SHIM"; mkdir -p "$SHIM/lib"
ln -s "$APP/Contents/Resources/python3.12" "$SHIM/lib/python3.12"

export PYTHONHOME="$SHIM"
export PYTHONPATH="$APP/Contents/Resources/python3.12/site-packages"
export DYLD_FRAMEWORK_PATH="$APP/Contents/Frameworks"
export QT_QPA_PLATFORM="${QT_QPA_PLATFORM:-offscreen}"
# Prefix must be the .app root: QGIS appends Contents/PlugIns/qgis to it when
# locating provider libraries.
export QGIS_PREFIX_PATH="$APP"

# PROJ and GDAL ship inside the bundle; without these the CRS database is not
# found and every EPSG lookup fails with "Cannot find proj.db".
export PROJ_DATA="$APP/Contents/Resources/qgis/proj"
export PROJ_LIB="$PROJ_DATA"
export GDAL_DATA="$APP/Contents/Resources/qgis/gdal"

# QGIS derives its provider path from the prefix and gets it wrong for this bundle
# (it resolves to MacOS/Contents/PlugIns/qgis). Without the real path the 'wms'
# provider never loads and XYZ basemap layers silently fail to construct.
export QGIS_PLUGINPATH="$APP/Contents/PlugIns/qgis"

exec "$APP/Contents/MacOS/python3.12" "$@"
