"""Verify build and DMG scripts refer to same bundle and embedded branding."""
from pathlib import Path
import re,plistlib
r=Path(__file__).parent
b=(r/'build-macos.sh').read_text()
p=(r/'package-macos.sh').read_text()
assert re.search(r'^APP="DPAS.app"$',b,re.M)
assert re.search(r'^APP="DPAS.app"$',p,re.M)
assert 'CFBundleDisplayName</key><string>DPAS</string>' in b
assert 'CFBundleName</key><string>Drucifer Plex Artwork Studio</string>' in b
assert 'CFBundleIconFile</key><string>AppIcon</string>' in b
assert 'AppIcon.icns' in b and 'AppIcon.icns' in p
assert 'hdiutil verify "$TMP_DMG"' in p
assert 'codesign --verify --deep --strict' in b and 'codesign --verify --deep --strict' in p
print('PASS: build/package bundle names match (DPAS.app)')
print('PASS: full application metadata and icon preserved')
print('PASS: DMG integrity and code signature checks present')
