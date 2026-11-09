from pathlib import Path
s=(Path(__file__).parent/'PASMacApp.swift').read_text()
a=s[s.index('private func selectRepository'):s.index('private let keychainService')]
r=s[s.index('private func restoreRepository'):s.index('private func selectRepository')]
assert 'let bookmark = try parent.bookmarkData' in a
assert a.index('let bookmark = try parent.bookmarkData') < a.index('repository = folder')
assert 'previousScope?.stopAccessingSecurityScopedResource()' in a
assert 'if accessing { parent.stopAccessingSecurityScopedResource() }' in a
assert 'let accessing = url.startAccessingSecurityScopedResource()' in r
assert 'isDirectory.boolValue' in r
assert 'scopedURL = accessing ? url : nil' in r
print('PASS: repository bookmark transaction and unsandboxed scope compatibility')
