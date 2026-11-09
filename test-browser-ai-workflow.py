"""Offline Chromium tests for AI preview/apply/restore and stale response handling.
Mocks the native message bridge; does not call OpenAI or assert macOS compatibility.
"""
from pathlib import Path
from playwright.sync_api import sync_playwright

with sync_playwright() as pw:
    browser=pw.chromium.launch(headless=True,executable_path=__import__('os').environ.get('DPAS_CHROMIUM_PATH') or ('/usr/bin/chromium' if __import__('os').path.isfile('/usr/bin/chromium') else None),args=['--no-sandbox'])
    page=browser.new_page(viewport={'width':1440,'height':900})
    errors=[]
    page.on('pageerror',lambda err: errors.append(str(err)))
    page.set_content((Path(__file__).parent/'index.html').read_text(),wait_until='load')
    page.evaluate('''async()=>{
      const c=document.createElement('canvas');c.width=40;c.height=60;
      c.getContext('2d').fillStyle='red';c.getContext('2d').fillRect(0,0,40,60);
      window.testOriginal=c.toDataURL('image/png');await setImage(window.testOriginal);
      c.getContext('2d').fillStyle='blue';c.getContext('2d').fillRect(0,0,40,60);
      window.testResult=c.toDataURL('image/png');
      window.webkit={messageHandlers:{pasNative:{postMessage:message=>{
        if(message.action==='openaiEdit'){
          window.pasNativeReply({id:message.id,ok:true,imageBase64:window.testResult.split(',')[1]});
        }
      }}}};
    }''')
    page.locator('#openaiEdit').click()
    page.wait_for_function('pendingAIImage!==null')
    assert not page.locator('#pasAICompare').is_hidden()
    page.locator('#openaiDiscard').click()
    assert page.evaluate('pendingAIImage===null && pendingAISourceImage===null && state.imageData===testOriginal')
    print('PASS: mocked AI preview/discard preserves original')
    page.locator('#openaiEdit').click()
    page.wait_for_function('pendingAIImage!==null')
    page.locator('#openaiApply').click()
    page.wait_for_function('state.imageData===testResult')
    assert page.locator('#openaiRestore').is_enabled()
    page.locator('#openaiRestore').click()
    page.wait_for_function('state.imageData===testOriginal')
    print('PASS: mocked AI apply/restore returns exact original')
    page.locator('#openaiEdit').click()
    page.wait_for_function('pendingAIImage!==null')
    page.evaluate('setImage(testResult)')
    page.locator('#openaiApply').click()
    page.wait_for_function("document.getElementById('openaiStatus').textContent.includes('Source artwork changed')")
    assert page.evaluate('state.imageData===testResult')
    assert page.evaluate('pendingAISourceImage===null && pendingAIImage===null')
    assert page.locator('#openaiDiscard').is_disabled()
    print('PASS: stale AI preview auto-discarded; controls disabled')
    assert not errors,errors
    browser.close()
