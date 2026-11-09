"""Release packaging must reuse the same validated build in CI."""
from pathlib import Path
r=Path(__file__).parent
package=(r/'package-macos.sh').read_text()
workflow=(r/'.github/workflows/macos-build.yml').read_text()
assert 'if [[ "${PAS_SKIP_BUILD:-0}" == "1" ]]' in package
assert 'bash verify-macos-app.sh' in package
assert 'bash build-macos.sh' in package
assert 'PAS_SKIP_BUILD=1 bash package-macos.sh 2>&1 | tee -a native-build.log' in workflow
assert workflow.index('bash verify-macos-app.sh 2>&1 | tee -a native-build.log') < workflow.index('PAS_SKIP_BUILD=1 bash package-macos.sh 2>&1 | tee -a native-build.log')
print('PASS: CI packages the previously compiled and verified DPAS.app')
print('PASS: direct packaging still performs a fresh build by default')
