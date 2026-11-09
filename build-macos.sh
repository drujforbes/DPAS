#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")"
APP="DPAS.app"
# Build in a staging folder so a failed compile cannot destroy a prior successful build.
STAGING="$(mktemp -d "${TMPDIR:-/tmp}/pas-build.XXXXXX")"
trap 'rm -rf "$STAGING"' EXIT
APP_PATH="$STAGING/$APP"
mkdir -p "$APP_PATH/Contents/MacOS" "$APP_PATH/Contents/Resources"
cat > "$APP_PATH/Contents/Info.plist" <<'PLIST'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
<key>CFBundleName</key><string>Drucifer Plex Artwork Studio</string>
<key>CFBundleDisplayName</key><string>DPAS</string>
<key>CFBundleIdentifier</key><string>com.plexartworkstudio.desktop</string>
<key>CFBundleIconFile</key><string>AppIcon</string>
<key>CFBundleExecutable</key><string>PlexArtworkStudio</string>
<key>CFBundlePackageType</key><string>APPL</string>
<key>CFBundleShortVersionString</key><string>0.2.0</string>
<key>CFBundleVersion</key><string>2</string>
<key>LSMinimumSystemVersion</key><string>13.0</string>
<key>NSHighResolutionCapable</key><true/>
</dict></plist>
PLIST
cp index.html "$APP_PATH/Contents/Resources/index.html"
ICON_ROOT="$(mktemp -d)"
ICONSET="$ICON_ROOT/AppIcon.iconset"
mkdir -p "$ICONSET"
for px in 16 32 128 256 512; do
  sips -s format png -z "$px" "$px" AppIcon.png --out "$ICONSET/icon_${px}x${px}.png" >/dev/null
  double=$((px * 2))
  sips -s format png -z "$double" "$double" AppIcon.png --out "$ICONSET/icon_${px}x${px}@2x.png" >/dev/null
done
iconutil -c icns "$ICONSET" -o "$APP_PATH/Contents/Resources/AppIcon.icns"
rm -rf "$ICON_ROOT"
xcrun swiftc -O -target arm64-apple-macos13.0 -framework SwiftUI -framework WebKit -framework AppKit -framework Security PASMacApp.swift -o "$APP_PATH/Contents/MacOS/PlexArtworkStudio"
chmod +x "$APP_PATH/Contents/MacOS/PlexArtworkStudio"
plutil -lint "$APP_PATH/Contents/Info.plist"
# Use ad-hoc signing for local execution. Distribution signing is a separate step.
codesign --force --deep --sign - "$APP_PATH"
# Verify the staged binary before touching the previously working application.
codesign --verify --deep --strict "$APP_PATH"
file "$APP_PATH/Contents/MacOS/PlexArtworkStudio" | grep -q 'arm64'
BACKUP="$STAGING/previous.app"
if [ -e "$APP" ]; then mv "$APP" "$BACKUP"; fi
if ! mv "$APP_PATH" "$APP"; then
  echo "Installation failed; restoring previous application." >&2
  if [ -e "$BACKUP" ]; then mv "$BACKUP" "$APP"; fi
  exit 1
fi
# Keep the prior build as a recoverable local backup until explicitly replaced.
if [ -e "$BACKUP" ]; then
  if [ -e "$APP.previous" ]; then rm -rf "$APP.previous"; fi
  mv "$BACKUP" "$APP.previous"
fi
echo "Built: $PWD/$APP"
echo "Locally ad-hoc signed build; public distribution requires Developer ID signing and notarization."
