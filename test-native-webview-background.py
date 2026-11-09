"""Ensure WebKit background configuration uses a supported public API."""
from pathlib import Path
s=(Path(__file__).parent/'PASMacApp.swift').read_text()
assert 'webView.underPageBackgroundColor = .clear' in s
assert 'setValue(false, forKey: "drawsBackground")' not in s
assert 'webView.loadFileURL(url, allowingReadAccessTo:' in s
print('PASS: WebKit background uses public macOS API')
