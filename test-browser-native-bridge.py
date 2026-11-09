"""Actual Chromium checks for native bridge timeout, late replies, and transport errors."""
from pathlib import Path
from playwright.sync_api import sync_playwright
with sync_playwright() as pw:
 browser=pw.chromium.launch(headless=True,executable_path=__import__('os').environ.get('DPAS_CHROMIUM_PATH') or ('/usr/bin/chromium' if __import__('os').path.isfile('/usr/bin/chromium') else None),args=['--no-sandbox'])
 page=browser.new_page()
 page.set_content((Path(__file__).parent/'index.html').read_text(),wait_until='load')
 result=page.evaluate("""async()=>{
   window.webkit={messageHandlers:{pasNative:{postMessage:m=>{window.lastNativeId=m.id;}}}};
   let error='';try{await pasNative('test',{},30)}catch(e){error=e.message}
   const empty=pasNativePending.size===0;
   pasNativeReply({id:window.lastNativeId,ok:true,message:'late reply'});
   return {error,empty,lateIgnored:pasNativePending.size===0};
 }""")
 assert 'timed out' in result['error'] and result['empty'] and result['lateIgnored'],result
 print('PASS: timed-out native request cleaned up; late reply ignored')
 result=page.evaluate("""async()=>{
   window.webkit.messageHandlers.pasNative.postMessage=()=>{throw Error('Bridge unavailable')};
   let error='';try{await pasNative('test',{},100)}catch(e){error=e.message}
   return {error,empty:pasNativePending.size===0};
 }""")
 assert 'Bridge unavailable' in result['error'] and result['empty'],result
 print('PASS: synchronous bridge failure cleaned up')
 result=page.evaluate("""async()=>{
   delete window.webkit;
   let error='';try{await pasNative('test',{},30)}catch(e){error=e.message}
   return error;
 }""")
 assert 'unavailable' in result,result
 print('PASS: missing native bridge rejects with actionable error')
 browser.close()
