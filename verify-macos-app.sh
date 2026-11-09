#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")"
APP="DPAS.app"
[[ "$(uname -s)" == "Darwin" ]] || { echo "Requires macOS" >&2; exit 1; }
[[ "$(uname -m)" == "arm64" ]] || { echo "Requires Apple Silicon" >&2; exit 1; }
[[ -x "$APP/Contents/MacOS/PlexArtworkStudio" ]] || { echo "Missing executable" >&2; exit 1; }
[[ -f "$APP/Contents/Resources/AppIcon.icns" ]] || { echo "Missing icon" >&2; exit 1; }
[[ -f "$APP/Contents/Resources/index.html" ]] || { echo "Missing GUI" >&2; exit 1; }
plutil -lint "$APP/Contents/Info.plist"
codesign --verify --deep --strict --verbose=2 "$APP"
file "$APP/Contents/MacOS/PlexArtworkStudio" | grep -q arm64
/usr/libexec/PlistBuddy -c 'Print :CFBundleDisplayName' "$APP/Contents/Info.plist" | grep -qx DPAS
/usr/libexec/PlistBuddy -c 'Print :CFBundleName' "$APP/Contents/Info.plist" | grep -qx 'Drucifer Plex Artwork Studio'
grep -q 'Drucifer Plex Artwork Studio' "$APP/Contents/Resources/index.html"
echo 'PASS: DPAS app structure, signature, Apple Silicon binary, icon, and GUI branding'
