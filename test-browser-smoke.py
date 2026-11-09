"""Chromium smoke test for bundled PAS editor; no external network or API keys."""
from pathlib import Path
from playwright.sync_api import sync_playwright

page_url = 'http://pas.test/index.html'
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, executable_path=__import__('os').environ.get('DPAS_CHROMIUM_PATH') or ('/usr/bin/chromium' if __import__('os').path.isfile('/usr/bin/chromium') else None), args=['--no-sandbox'])
    page = browser.new_page(viewport={'width': 1440, 'height': 900})
    errors = []
    page.on('pageerror', lambda err: errors.append(str(err)))
    page.set_content((Path(__file__).parent / 'index.html').read_text(), wait_until='load')
    assert page.title() == 'Drucifer Plex Artwork Studio'
    assert page.locator('#format').count() == 1
    assert page.locator('#projectFile').count() == 1
    assert page.locator('#openaiEdit').count() == 1
    assert page.locator('#pasAICompare').count() == 1
    assert page.locator('#openaiRestore').count() == 1
    assert page.locator('canvas').count() >= 1
    assert page.evaluate("typeof validatePASProject === 'function'")
    assert page.evaluate("typeof pasValidEvidenceURL === 'function'")
    assert page.evaluate("pasValidEvidenceURL('https://www.oscars.org/oscars/ceremonies')")
    assert not page.evaluate("pasValidEvidenceURL('https://user:pass@example.com')")
    assert not page.evaluate("pasValidEvidenceURL('javascript:alert(1)')")
    page.locator('#format').select_option('background')
    assert page.locator('#format').input_value() == 'background'
    page.locator('#format').select_option('poster')
    assert page.locator('#format').input_value() == 'poster'
    page.locator('#awardCsv').set_input_files({'name':'invalid.csv','mimeType':'text/csv','buffer':b'award,outcome,source\nOSCAR,winner,https://example.com'})
    page.locator('#previewAwardCsv').evaluate('(el) => el.click()')
    page.wait_for_function("document.getElementById('awardImportStatus').textContent.includes('Required columns')")
    assert not errors, f'JavaScript errors on load and interactions: {errors}'
    print('PASS: browser load, controls, canvas, format switching, CSV rejection, validator, URL rules, zero page errors')
    browser.close()
