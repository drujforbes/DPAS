from pathlib import Path
p=Path(__file__).resolve().parent
script=(p/'test-macos-install.sh').read_text()
workflow=(p/'.github/workflows/macos-build.yml').read_text()
for token in ['hdiutil verify', 'hdiutil attach', 'ditto "$MOUNT/DPAS.app"', 'codesign --verify --deep --strict', 'PlistBuddy', 'AppIcon.icns', 'trap cleanup EXIT', 'readlink']:
    assert token in script, token
assert 'bash test-macos-install.sh 2>&1 | tee -a native-build.log' in workflow
assert "- 'test-macos-install.sh'" in workflow
assert 'bash -n build-macos.sh package-macos.sh verify-macos-app.sh test-macos-install.sh' in workflow
print('PASS: mounted-DMG installation smoke test and CI integration')
