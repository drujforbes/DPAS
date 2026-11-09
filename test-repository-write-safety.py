"""Static contract for repository write boundaries; native filesystem test still required."""
from pathlib import Path
s=(Path(__file__).parent/'PASMacApp.swift').read_text()
checks={
    'encoded payload bounded before decode': s.index('encoded.utf8.count <= 106_666_672') < s.index('let data = Data(base64Encoded:encoded)'),
    'decoded payload bounded': 'data.count < 80_000_000' in s,
    'directory symlinks resolved': 'directory.standardizedFileURL.resolvingSymlinksInPath()' in s,
    'resolved directory must remain direct child of repository': 'resolvedDirectory.deletingLastPathComponent() == root' in s,
    'symlink target rejected': 'values.isSymbolicLink == true' in s,
    'atomic write retained': 'data.write(to:target,options:.atomic)' in s,
}
for label, ok in checks.items(): print(('PASS' if ok else 'FAIL') + ': ' + label)
assert all(checks.values())
