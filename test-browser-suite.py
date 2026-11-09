#!/usr/bin/env python3
"""Run Chromium browser regressions concurrently with per-test isolation and timeouts."""
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
import os
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
# Exclude this orchestrator: running it as a child recursively starts more suites.
TESTS = sorted(t for t in ROOT.glob('test-browser-*.py') if t.name != Path(__file__).name)
TIMEOUT = int(os.environ.get('DPAS_BROWSER_TEST_TIMEOUT', '50'))
WORKERS = min(max(int(os.environ.get('DPAS_BROWSER_WORKERS', '3')), 1), 4)


def run_one(test):
    try:
        proc = subprocess.run([sys.executable, str(test)], cwd=ROOT,
                              capture_output=True, text=True, timeout=TIMEOUT)
        return test.name, proc.returncode == 0, (proc.stdout + '\n' + proc.stderr).strip()
    except subprocess.TimeoutExpired as exc:
        return test.name, False, f'Timed out after {TIMEOUT}s: {exc}'


def main():
    if not TESTS:
        sys.exit('ERROR: no browser regression tests found')
    failed = []
    with ThreadPoolExecutor(max_workers=WORKERS) as pool:
        futures = {pool.submit(run_one, test): test for test in TESTS}
        for future in as_completed(futures):
            name, passed, detail = future.result()
            print(f"{'PASS' if passed else 'FAIL'}: {name}", flush=True)
            if not passed:
                failed.append(name)
                print(detail[-1800:], file=sys.stderr, flush=True)
    print(f'Browser suite: {len(TESTS)-len(failed)}/{len(TESTS)} passed')
    if failed:
        sys.exit(1)


if __name__ == '__main__':
    main()
