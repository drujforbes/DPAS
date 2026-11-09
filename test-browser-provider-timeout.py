from pathlib import Path
from playwright.sync_api import sync_playwright
with sync_playwright() as pw:
 b=pw.chromium.launch(headless=True,executable_path=__import__('os').environ.get('DPAS_CHROMIUM_PATH') or ('/usr/bin/chromium' if __import__('os').path.isfile('/usr/bin/chromium') else None),args=['--no-sandbox'])
 p=b.new_page()
 p.set_content((Path(__file__).parent/'index.html').read_text())
 p.evaluate('''() => {
   window.fetch=(url,opts)=>new Promise((resolve,reject)=>{
      opts.signal.addEventListener('abort',()=>reject(new DOMException('Aborted','AbortError')));
   });
   document.getElementById('token').value='test';
 }''')
 p.locator('#query').fill('Stalled title')
 p.evaluate('''async () => {window.timeoutResult=await providerFetch('https://example.org',{},35).then(()=> 'unexpected',e=>e.message)}''')
 assert 'timed out' in p.evaluate('timeoutResult')
 # Check search status with accelerated provider timeout while retaining production 18s default.
 p.evaluate('''() => { window.originalProviderFetch=providerFetch;providerFetch=(url,opts)=>originalProviderFetch(url,opts,35);search();}''')
 p.wait_for_function("document.getElementById('status').textContent.includes('timed out')",timeout=5000)
 print('PASS: stalled provider request times out and search displays actionable error')
 b.close()
