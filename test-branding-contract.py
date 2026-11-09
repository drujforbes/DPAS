from pathlib import Path
import re, plistlib, subprocess
from PIL import Image
root=Path(__file__).resolve().parent
html=(root/'index.html').read_text()
build=(root/'build-macos.sh').read_text()
assert re.search(r'<h1>Drucifer Plex Artwork Studio</h1>',html), 'Full GUI title missing'
assert '<title>Drucifer Plex Artwork Studio</title>' in html
assert 'APP="DPAS.app"' in build
assert '<key>CFBundleDisplayName</key><string>DPAS</string>' in build
assert '<key>CFBundleName</key><string>Drucifer Plex Artwork Studio</string>' in build
assert 'iconutil -c icns' in build
with Image.open(root/'AppIcon.png') as icon:
    assert icon.size==(1024,1024) and icon.mode=='RGBA'
print('PASS: full GUI title and browser title retained')
print('PASS: installed app and display label use DPAS')
print('PASS: 1024x1024 icon and macOS icon build step present')
