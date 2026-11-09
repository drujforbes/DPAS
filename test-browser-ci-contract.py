from pathlib import Path
r=Path(__file__).parent
workflow=(r/'.github/workflows/macos-build.yml').read_text()
runner=(r/'test-browser-suite.py').read_text()
assert 'browser-regression:' in workflow
assert 'needs: browser-regression' in workflow
assert 'ubuntu-24.04' in workflow
assert '.venv/bin/python -m playwright install --with-deps chromium' in workflow
assert 'apt-get install -y chromium' not in workflow
for script in r.glob('test-browser-*.py'):
    if "chromium.launch(" in script.read_text():
        assert 'DPAS_CHROMIUM_PATH' in script.read_text(), script.name
assert '.venv/bin/python -m pip install playwright' in workflow
assert '.venv/bin/python test-browser-suite.py' in workflow
assert "glob('test-browser-*.py')" in runner
assert 'timeout=TIMEOUT' in runner and 'ThreadPoolExecutor' in runner
assert 'if failed:' in runner
print('PASS: browser regression CI gates the Apple Silicon build')
