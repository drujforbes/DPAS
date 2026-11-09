"""Offline Chromium functional regression: actual PNG generation, preview controls, project import."""
from pathlib import Path
from playwright.sync_api import sync_playwright

with sync_playwright() as pw:
 browser=pw.chromium.launch(headless=True,executable_path=__import__('os').environ.get('DPAS_CHROMIUM_PATH') or ('/usr/bin/chromium' if __import__('os').path.isfile('/usr/bin/chromium') else None),args=['--no-sandbox'])
 page=browser.new_page(viewport={'width':1440,'height':900})
 errors=[]
 page.on('pageerror',lambda e:errors.append(str(e)))
 page.set_content((Path(__file__).parent/'index.html').read_text(),wait_until='load')
 # Load a synthetic local artwork through the actual editor's setImage function.
 page.evaluate("""async()=>{const c=document.createElement('canvas');c.width=100;c.height=150;c.getContext('2d').fillRect(0,0,100,150);await setImage(c.toDataURL('image/png'));}""")
 assert '100 × 150' in page.locator('#exportQuality').inner_text()
 for kind,scale,expected in [('poster','1',[1000,1500]),('poster','2',[2000,3000]),('background','1',[1920,1080]),('background','2',[3840,2160])]:
  page.locator('#format').select_option(kind)
  page.locator('#exportScale').select_option(scale)
  dimensions=page.evaluate("""async()=>{const blob=await makeExportPNG();const bitmap=await createImageBitmap(blob);const result=[bitmap.width,bitmap.height];bitmap.close();return result;}""")
  assert dimensions==expected,(kind,scale,dimensions)
  assert page.evaluate('renderScale')==1
  print('PASS: exported',kind,scale,dimensions)
 # Discard AI preview should not replace original and must clear stale request identity.
 page.evaluate("""()=>{pendingAISourceImage=state.image;pendingAIOriginal=state.imageData;pendingAIImage=state.imageData;document.getElementById('openaiDiscard').disabled=false;}""")
 page.locator('#openaiDiscard').click()
 assert page.evaluate('pendingAIImage===null && pendingAISourceImage===null')
 # Reject invalid project through the actual file input.
 page.locator('#projectFile').set_input_files({'name':'bad.json','mimeType':'application/json','buffer':b'{"version":999,"format":"poster"}'})
 page.wait_for_function("document.getElementById('status').textContent.includes('Project import rejected')")
 assert page.evaluate('state.image!==null')
 assert not errors,errors
 print('PASS: AI discard, invalid project rejection, no uncaught browser errors')
 browser.close()
