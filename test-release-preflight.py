"""Portable release preflight: fail before spending time on macOS compilation."""
from pathlib import Path
import subprocess, sys, re
root = Path(__file__).resolve().parent
checks = [
 ('Bundled editor JavaScript syntax', [sys.executable, 'test-editor-javascript.py']),
 ('WebKit public background API', [sys.executable, 'test-native-webview-background.py']),
 ('Native HTTP and file chooser safety', [sys.executable, 'test-native-http-and-file-panel.py']),
 ('Native external browser links', [sys.executable, 'test-native-external-links.py']),
 ('Keychain update safety', [sys.executable, 'test-native-keychain-update.py']),
 ('Repository switch safety', [sys.executable, 'test-native-repository-switch.py']),
 ('Repository write boundary', [sys.executable, 'test-repository-write-safety.py']),
 ('Native build diagnostics', [sys.executable, 'test-native-build-diagnostics.py']),
 ('Browser suite recursion guard', [sys.executable, 'test-browser-suite-contract.py']),
 ('DMG SHA-256 integrity', [sys.executable, 'test-release-checksum.py']),
 ('Provider integration contracts', [sys.executable, 'test-live-provider-contract.py']),
 ('DMG installation test contract', [sys.executable, 'test-install-contract.py']),
 ('Build-to-package consistency', [sys.executable, 'test-packaging-reuse.py']),
 ('macOS packaging', [sys.executable, 'test-macos-packaging-contract.py']),
 ('macOS CI workflow', [sys.executable, 'test-ci-contract.py']),
 ('Branding', [sys.executable, 'test-branding-contract.py']),
 ('Native OpenAI contract', [sys.executable, 'test-native-openai-contract.py']),
 ('Native PNG input limits', [sys.executable, 'test-native-image-dimensions.py']),
 ('Native PNG output limits', [sys.executable, 'test-native-output-image-validation.py']),
 ('Project import', ['node', 'test-project-import.cjs']),
 ('Award CSV', ['node', 'test-award-csv-validation.cjs']),
 ('Award evidence URLs', ['node', 'test-award-url-consistency.cjs']),
 ('Company logo selection', ['node', 'test-company-logo-stale.cjs']),
 ('Image load races', ['node', 'test-image-load-race.cjs']),
 ('Provider connection timeouts', ['node', 'test-provider-connection-timeouts.cjs']),
 ('Title metadata reset', ['node', 'test-title-metadata-reset.cjs']),
]
failures=[]
for label, cmd in checks:
    result=subprocess.run(cmd, cwd=root, capture_output=True, text=True, timeout=30)
    print(f"{'PASS' if result.returncode == 0 else 'FAIL'}: {label}", flush=True)
    if result.returncode:
        failures.append((label, (result.stdout+'\n'+result.stderr)[-2000:]))
for label, detail in failures: print(f'\n{label}:\n{detail}',file=sys.stderr)
if failures: sys.exit(1)
print(f'PASS: {len(checks)} release preflight checks')
