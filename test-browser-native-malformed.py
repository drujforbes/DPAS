"""Actual browser checks for malformed native bridge replies."""
from pathlib import Path
from playwright.sync_api import sync_playwright
with sync_playwright() as pw:
 browser=pw.chromium.launch(headless=True,executable_path=__import__('os').environ.get('DPAS_CHROMIUM_PATH') or ('/usr/bin/chromium' if __import__('os').path.isfile('/usr/bin/chromium') else None),args=['--no-sandbox'])
 page=browser.new_page()
 errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 page.set_content((Path(__file__).parent/'index.html').read_text(),wait_until='load')
 result=page.evaluate("""async()=>{
   window.webkit={messageHandlers:{pasNative:{postMessage:m=>{window.nativeId=m.id;}}}};
   pasNativeReply(null);pasNativeReply(undefined);pasNativeReply({});
   const request=pasNative('test',{},1000);
   pasNativeReply({id:window.nativeId,ok:true});
   let error='';try{await request}catch(e){error=e.message}
   return {error,pending:pasNativePending.size};
 }""")
 assert 'missing expected data' in result['error'] and result['pending']==0,result
 print('PASS: malformed replies rejected and pending state cleaned')
 result=page.evaluate("""async()=>{
   const request=pasNative('test',{},1000);
   pasNativeReply({id:window.nativeId,ok:false,message:{secret:'bad object'}});
   let error='';try{await request}catch(e){error=e.message}
   return {error,pending:pasNativePending.size};
 }""")
 assert result['error']=='Native request failed.' and result['pending']==0,result
 print('PASS: non-string native error payload safely normalized')
 assert not errors,errors
 browser.close()
