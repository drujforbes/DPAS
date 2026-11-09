"""Regression contract for WKWebView external links opened via window.open."""
from pathlib import Path
s=Path(__file__).with_name('PASMacApp.swift').read_text()
h=Path(__file__).with_name('index.html').read_text()
assert "window.open(base(q),'_blank','noopener,noreferrer')" in h
assert 'createWebViewWith configuration: WKWebViewConfiguration' in s
start=s.index('func webView(_ webView: WKWebView,\n                     createWebViewWith')
end=s.index('func webView(_ webView: WKWebView, runOpenPanelWith',start)
body=s[start:end]
for expected in ['navigationAction.targetFrame == nil','isBundledEditor(webView.url)',
                 'navigationAction.sourceFrame.isMainFrame',
                 'isBundledEditor(navigationAction.sourceFrame.request.url)',
                 '["http", "https"].contains(scheme)', 'NSWorkspace.shared.open(url)', 'return nil']:
    assert expected in body, expected
assert 'WKWebView(frame:' not in body
print('PASS: native external links delegate and origin/scheme checks')
