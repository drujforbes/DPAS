from pathlib import Path
import importlib.util
root=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('dpas_suite',root/'test-browser-suite.py')
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
assert m.TESTS
assert all(t.name != 'test-browser-suite.py' for t in m.TESTS)
assert len(m.TESTS)==len(list(root.glob('test-browser-*.py')))-1
assert len(set(m.TESTS))==len(m.TESTS)
print(f'PASS: {len(m.TESTS)} browser tests discovered without recursive suite execution')
