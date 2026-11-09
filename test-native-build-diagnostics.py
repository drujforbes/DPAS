from pathlib import Path
s=(Path(__file__).parent/'.github/workflows/macos-build.yml').read_text()
assert 'set -o pipefail' in s
assert 'bash build-macos.sh 2>&1 | tee native-build.log' in s
assert 'PAS_SKIP_BUILD=1 bash package-macos.sh 2>&1 | tee -a native-build.log' in s
assert 'if: always()' in s
assert 'DPAS-native-build-diagnostics' in s
assert 'path: native-build.log' in s
print('PASS: build logs preserved on failure, without masking command exit codes')
