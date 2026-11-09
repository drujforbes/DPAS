from pathlib import Path
p=Path(__file__).parent
s=(p/'.github/workflows/macos-build.yml').read_text()
assert 'runs-on: macos-15' in s
assert s.count("- 'test-*.py'") == 2
assert s.count("- 'test-*.cjs'") == 2
assert 'python3 test-release-preflight.py' in s
assert 'swiftc -frontend -parse PASMacApp.swift' in s
assert 'bash build-macos.sh' in s
assert 'bash verify-macos-app.sh' in s
assert 'bash package-macos.sh' in s
assert 'bash test-macos-install.sh 2>&1 | tee -a native-build.log' in s
install=(p/'test-macos-install.sh').read_text()
assert 'hdiutil attach' in install and 'hdiutil detach' in install
assert 'DPAS.app' in install
assert 'upload-artifact@v4' in s
assert 'PAS_SIGN_IDENTITY' not in s and 'PAS_NOTARY_PROFILE' not in s
print('PASS: Apple Silicon CI builds, verifies, mounts and uploads test DMG without secrets')
