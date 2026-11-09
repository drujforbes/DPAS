from pathlib import Path
s=(Path(__file__).parent/'PASMacApp.swift').read_text()
start=s.index('private func storeAPIKey(')
end=s.index('private func replyImage(',start)
body=s[start:end]
assert 'SecItemUpdate(q as CFDictionary, updates as CFDictionary)' in body
assert 'updateStatus != errSecItemNotFound { return false }' in body
assert 'SecItemAdd(attributes as CFDictionary, nil)' in body
assert body.index('if value.isEmpty') < body.index('SecItemDelete(q as CFDictionary)')
assert body.count('SecItemDelete(q as CFDictionary)') == 1
assert 'let saved = storeAPIKey(key)' in s
assert 'existing credential was preserved' in s
print('PASS: Keychain credential updates are non-destructive and failures are accurately reported')
