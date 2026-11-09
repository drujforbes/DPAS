#!/usr/bin/env python3
"""Parse every inline editor script using Node's JavaScript parser.

This catches malformed bundled editor code before a costly native macOS build.
"""
from html.parser import HTMLParser
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parent

class Scripts(HTMLParser):
    def __init__(self):
        super().__init__()
        self.inside = False
        self.inline = False
        self.fragments = []
        self.scripts = []

    def handle_starttag(self, tag, attrs):
        if tag == 'script':
            attributes = dict(attrs)
            self.inside = True
            self.inline = 'src' not in attributes and attributes.get('type', 'text/javascript') in ('text/javascript', 'module', '')
            self.fragments = []

    def handle_data(self, data):
        if self.inside and self.inline:
            self.fragments.append(data)

    def handle_endtag(self, tag):
        if tag == 'script' and self.inside:
            if self.inline:
                self.scripts.append(''.join(self.fragments))
            self.inside = False
            self.inline = False

parser = Scripts()
parser.feed((ROOT / 'index.html').read_text(encoding='utf-8'))
if not parser.scripts or not any(s.strip() for s in parser.scripts):
    sys.exit('FAIL: no inline JavaScript found in bundled editor')
for index, script in enumerate(parser.scripts, 1):
    with tempfile.TemporaryDirectory(prefix='dpas-js-') as temp:
        path = Path(temp) / f'editor-{index}.mjs'
        path.write_text(script, encoding='utf-8')
        result = subprocess.run(['node', '--check', str(path)], capture_output=True, text=True)
        if result.returncode:
            sys.exit(f'FAIL: inline script {index} invalid:\n{result.stderr}')
print(f'PASS: {len(parser.scripts)} bundled editor script(s) parse as JavaScript')
