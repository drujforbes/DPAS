"""Release integrity contract checks (portable; no macOS required)."""
from pathlib import Path
r=Path(__file__).parent
pkg=(r/'package-macos.sh').read_text()
install=(r/'test-macos-install.sh').read_text()
workflow=(r/'.github/workflows/macos-build.yml').read_text()
assert 'shasum -a 256 "$OUT" > "$OUT.sha256"' in pkg
assert 'shasum -a 256 -c "$OUT.sha256"' in pkg
assert 'shasum -a 256 -c "$(basename "$DMG").sha256"' in install
assert 'Drucifer_Plex_Artwork_Studio_Apple_Silicon.dmg.sha256' in workflow
assert 'hdiutil verify "$DMG"' in install
print('PASS: checksum created, verified before mounting, and published with DMG')
