from pathlib import Path
import re, struct
root=Path(__file__).resolve().parent
html=(root/'index.html').read_text()
build=(root/'build-macos.sh').read_text()
assert re.search(r'<h1>Drucifer Plex Artwork Studio</h1>',html), 'Full GUI title missing'
assert '<title>Drucifer Plex Artwork Studio</title>' in html
assert 'APP="DPAS.app"' in build
assert '<key>CFBundleDisplayName</key><string>DPAS</string>' in build
assert '<key>CFBundleName</key><string>Drucifer Plex Artwork Studio</string>' in build
assert 'iconutil -c icns' in build
# Check PNG IHDR using Python's standard library. CI must not depend on Pillow.
with (root/'AppIcon.png').open('rb') as icon:
    header = icon.read(33)
assert header[:8] == b'\x89PNG\r\n\x1a\n', 'Icon is not a PNG'
assert header[12:16] == b'IHDR', 'PNG IHDR missing'
width, height, bit_depth, color_type = struct.unpack('>IIBB', header[16:26])
assert (width, height, bit_depth, color_type) == (1024, 1024, 8, 6), 'Expected 1024x1024 8-bit RGBA icon'
print('PASS: full GUI title and browser title retained')
print('PASS: installed app and display label use DPAS')
print('PASS: 1024x1024 icon and macOS icon build step present')
