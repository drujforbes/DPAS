"""Browser regression for malformed AI replies, concurrent edits, and retry."""
from pathlib import Path
from playwright.sync_api import sync_playwright
with sync_playwright() as pw:
    browser=pw.chromium.launch(headless=True,executable_path=__import__('os').environ.get('DPAS_CHROMIUM_PATH') or ('/usr/bin/chromium' if __import__('os').path.isfile('/usr/bin/chromium') else None),args=['--no-sandbox'])
    page=browser.new_page()
    errors=[]
    page.on('pageerror',lambda e:errors.append(str(e)))
    page.set_content((Path(__file__).parent/'index.html').read_text(),wait_until='load')
    page.evaluate("""async()=>{
      const c=document.createElement('canvas');c.width=30;c.height=45;
      c.getContext('2d').fillStyle='red';c.getContext('2d').fillRect(0,0,30,45);
      window.original=c.toDataURL('image/png');
      await setImage(window.original);
      window.requests=[];
      window.webkit={messageHandlers:{pasNative:{postMessage:m=>{if(m.action==='openaiEdit')window.requests.push(m);}}}};
    }""")
    page.locator('#openaiEdit').click()
    page.wait_for_function('requests.length===1')
    assert page.locator('#openaiEdit').is_disabled()
    page.evaluate("""pasNativeReply({id:requests[0].id,ok:true,imageBase64:'not-an-image'})""")
    page.wait_for_function("document.getElementById('openaiStatus').textContent.includes('failed')")
    assert page.locator('#openaiApply').is_disabled()
    assert page.locator('#openaiEdit').is_enabled()
    assert page.evaluate('state.imageData===original && pendingAIImage===null')
    print('PASS: malformed AI image rejected without modifying artwork')
    page.locator('#openaiEdit').click()
    page.wait_for_function('requests.length===2')
    page.evaluate("""pasNativeReply({id:requests[1].id,ok:false,message:'Rate limit test'})""")
    page.wait_for_function("document.getElementById('openaiStatus').textContent.includes('Rate limit test')")
    assert page.locator('#openaiEdit').is_enabled()
    assert page.evaluate('state.imageData===original')
    print('PASS: API error reported and retry enabled')
    assert not errors,errors
    browser.close()
