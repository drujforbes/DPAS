"""Static contract checks for native image-service failures and file chooser access."""
from pathlib import Path
s=Path(__file__).with_name('PASMacApp.swift').read_text()
assert 'guard let http = response as? HTTPURLResponse else' in s
assert s.index('if !(200...299).contains(http.statusCode)') < s.index('guard let obj = (try? JSONSerialization.jsonObject(with:responseData))')
assert 'HTTP \\(http.statusCode): \\(description)' in s
assert 'The image service rejected the request.' in s
assert 'guard frame.isMainFrame, isBundledEditor(frame.request.url)' in s
assert 'completionHandler(nil)' in s
print('PASS: HTTP failure handling and privileged file chooser gating')
