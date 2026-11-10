#!/bin/bash
# Local Apple Silicon fallback when hosted macOS runners cannot be allocated.
# Run from Terminal: bash build-on-my-mac.sh
set -euo pipefail
cd "$(dirname "$0")"

if [[ "$(uname -s)" != "Darwin" || "$(uname -m)" != "arm64" ]]; then
  echo "This native installer build requires an Apple Silicon Mac." >&2
  exit 1
fi
if ! command -v xcrun >/dev/null || ! xcrun --find swiftc >/dev/null 2>&1; then
  echo "Apple's developer command-line tools are required." >&2
  echo "Run: xcode-select --install" >&2
  exit 1
fi
for f in PASMacApp.swift index.html AppIcon.png build-macos.sh package-macos.sh verify-macos-app.sh test-macos-install.sh; do
  [[ -f "$f" ]] || { echo "Missing required file: $f" >&2; exit 1; }
done
echo "DPAS: Checking native Swift grammar..."
xcrun swiftc -frontend -parse PASMacApp.swift
echo "DPAS: Checking packaging shell scripts..."
bash -n build-macos.sh package-macos.sh verify-macos-app.sh test-macos-install.sh
if command -v python3 >/dev/null && command -v node >/dev/null; then
  echo "DPAS: Running source preflight..."
  python3 test-release-preflight.py
else
  echo "DPAS: Optional automated preflight skipped (Python 3 or Node.js unavailable)."
  echo "Native compiler, signing and DMG installation checks will still run."
fi
echo "DPAS: Compiling arm64 native application and packaging DMG..."
bash package-macos.sh
echo "DPAS: Testing installation from completed DMG..."
bash test-macos-install.sh
echo ""
echo "SUCCESS: Native DPAS Mac installer built, signed ad hoc, and install-tested."
echo "DMG: $PWD/Drucifer_Plex_Artwork_Studio_Apple_Silicon.dmg"
echo "SHA-256: $PWD/Drucifer_Plex_Artwork_Studio_Apple_Silicon.dmg.sha256"
echo "For personal use, Finder may require Open or Privacy & Security > Open Anyway."
