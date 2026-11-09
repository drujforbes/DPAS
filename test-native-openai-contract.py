from pathlib import Path
s=(Path(__file__).parent/'PASMacApp.swift').read_text()
checks={
 'pre-decode encoded size limit':s.index('image.utf8.count <= 27_000_000')<s.index('Data(base64Encoded:image)'),
 'decoded payload size limit':'data.count <= 20_000_000' in s,
 'PNG signature validation':'data.starts(with: [137,80,78,71,13,10,26,10])' in s,
 'prompt size validation':'cleanedPrompt.utf8.count <= 12_000' in s,
 'ephemeral session':'URLSessionConfiguration.ephemeral' in s,
 'Keychain credential storage':'SecItemAdd' in s,
 'error status parsing':'HTTPURLResponse' in s,
}
for name,ok in checks.items():
 print(('PASS' if ok else 'FAIL')+': '+name)
assert all(checks.values())
