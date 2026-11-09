#!/bin/bash
# Verify the DMG can be mounted and the bundled app copied to a fresh install location.
set -euo pipefail
cd "$(dirname "$0")"
DMG="${1:-Drucifer_Plex_Artwork_Studio_Apple_Silicon.dmg}"
[[ "$(uname -s)" == "Darwin" ]] || { echo 'Requires macOS' >&2; exit 1; }
[[ "$(uname -m)" == "arm64" ]] || { echo 'Requires Apple Silicon' >&2; exit 1; }
[[ -f "$DMG" ]] || { echo "Missing DMG: $DMG" >&2; exit 1; }
# If a release checksum accompanies the DMG, verify it before mounting.
if [[ -f "$DMG.sha256" ]]; then
  (cd "$(dirname "$DMG")" && shasum -a 256 -c "$(basename "$DMG").sha256")
fi
WORK="$(mktemp -d "${TMPDIR:-/tmp}/dpas-install.XXXXXX")"
MOUNT="$WORK/mounted"
ATTACHED=0
cleanup() {
  if [[ "$ATTACHED" == 1 ]]; then hdiutil detach "$MOUNT" -quiet || true; fi
  rm -rf "$WORK"
}
trap cleanup EXIT
mkdir -p "$MOUNT" "$WORK/Applications"
hdiutil verify "$DMG"
hdiutil attach "$DMG" -mountpoint "$MOUNT" -nobrowse -readonly -quiet
ATTACHED=1
[[ -d "$MOUNT/DPAS.app" && -L "$MOUNT/Applications" ]] || { echo 'DMG layout incomplete' >&2; exit 1; }
[[ "$(readlink "$MOUNT/Applications")" == '/Applications' ]] || { echo 'Applications shortcut points elsewhere' >&2; exit 1; }
ditto "$MOUNT/DPAS.app" "$WORK/Applications/DPAS.app"
APP="$WORK/Applications/DPAS.app"
[[ -x "$APP/Contents/MacOS/PlexArtworkStudio" ]] || { echo 'Executable missing after copy' >&2; exit 1; }
[[ -s "$APP/Contents/Resources/AppIcon.icns" ]] || { echo 'Icon missing after copy' >&2; exit 1; }
codesign --verify --deep --strict --verbose=2 "$APP"
file "$APP/Contents/MacOS/PlexArtworkStudio" | grep -q arm64
/usr/libexec/PlistBuddy -c 'Print :CFBundleDisplayName' "$APP/Contents/Info.plist" | grep -qx DPAS
/usr/libexec/PlistBuddy -c 'Print :CFBundleName' "$APP/Contents/Info.plist" | grep -qx 'Drucifer Plex Artwork Studio'
grep -q 'Drucifer Plex Artwork Studio' "$APP/Contents/Resources/index.html"
echo 'PASS: DMG mounted; DPAS.app copied and verified with correct branding, icon, signature and architecture'
