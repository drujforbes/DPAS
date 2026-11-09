#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")"
if [[ "$(uname -s)" != "Darwin" ]]; then echo "Run on macOS." >&2; exit 1; fi
if [[ "$(uname -m)" != "arm64" ]]; then echo "Apple Silicon (arm64) required." >&2; exit 1; fi
for cmd in xcrun sips iconutil hdiutil codesign plutil file; do
  command -v "$cmd" >/dev/null || { echo "Missing: $cmd" >&2; exit 1; }
done
# Reuse the already compiled and verified app in CI. The default remains
# a fresh build for developers invoking this packaging script directly.
if [[ "${PAS_SKIP_BUILD:-0}" == "1" ]]; then
  bash verify-macos-app.sh
else
  bash build-macos.sh
fi
APP="DPAS.app"
if [[ -n "${PAS_SIGN_IDENTITY:-}" ]]; then
  codesign --force --deep --options runtime --timestamp --sign "$PAS_SIGN_IDENTITY" "$APP"
fi
[[ -d "$APP/Contents/MacOS" && -f "$APP/Contents/Resources/AppIcon.icns" ]] || { echo "Incomplete DPAS.app bundle." >&2; exit 1; }
codesign --verify --deep --strict --verbose=2 "$APP"
plutil -lint "$APP/Contents/Info.plist"
file "$APP/Contents/MacOS/PlexArtworkStudio"
OUT="Drucifer_Plex_Artwork_Studio_Apple_Silicon.dmg"
RELEASE_DIR="$(mktemp -d "${TMPDIR:-/tmp}/dpas-release.XXXXXX")"
trap 'rm -rf "$RELEASE_DIR"' EXIT
# A standard drag-to-Applications DMG layout. Avoid altering the working .app.
mkdir -p "$RELEASE_DIR/install"
cp -R "$APP" "$RELEASE_DIR/install/DPAS.app"
ln -s /Applications "$RELEASE_DIR/install/Applications"
TMP_DMG="$RELEASE_DIR/DPAS.dmg"
hdiutil create -volname "Drucifer Plex Artwork Studio" -srcfolder "$RELEASE_DIR/install" -ov -format UDZO "$TMP_DMG"
hdiutil verify "$TMP_DMG"
# Notarization is optional, but requires Developer ID signing and a configured
# keychain profile created with `xcrun notarytool store-credentials`.
if [[ -n "${PAS_NOTARY_PROFILE:-}" ]]; then
  [[ -n "${PAS_SIGN_IDENTITY:-}" ]] || { echo "Notarization requires PAS_SIGN_IDENTITY." >&2; exit 1; }
  xcrun notarytool submit "$TMP_DMG" --keychain-profile "$PAS_NOTARY_PROFILE" --wait
  xcrun stapler staple "$TMP_DMG"
  xcrun stapler validate "$TMP_DMG"
fi
# Publish only after integrity checks and any requested notarization succeed.
mv -f "$TMP_DMG" "$OUT"
# Produce a reproducible integrity record alongside the exact published DMG.
# shasum's default output includes the file name; -c can verify it later.
shasum -a 256 "$OUT" > "$OUT.sha256"
shasum -a 256 -c "$OUT.sha256"
echo "Package ready: $PWD/$OUT"
echo "SHA-256 checksum: $PWD/$OUT.sha256"
if [[ -z "${PAS_SIGN_IDENTITY:-}" ]]; then
  echo "Local ad-hoc signed build; not notarized or ready for public distribution."
else
  if [[ -n "${PAS_NOTARY_PROFILE:-}" ]]; then
    echo "Developer ID signed, notarized, and stapled."
  else
    echo "Developer ID signed. Set PAS_NOTARY_PROFILE to notarize."
  fi
fi
