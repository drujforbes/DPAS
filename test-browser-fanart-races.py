from pathlib import Path
from playwright.sync_api import sync_playwright
with sync_playwright() as pw:
 browser=pw.chromium.launch(headless=True,executable_path=__import__('os').environ.get('DPAS_CHROMIUM_PATH') or ('/usr/bin/chromium' if __import__('os').path.isfile('/usr/bin/chromium') else None),args=['--no-sandbox'])
 page=browser.new_page()
 page.set_content((Path(__file__).parent/'index.html').read_text(),wait_until='load')
 page.evaluate('''()=>{
  window.pendingGallery=[];window.pendingFanart=[];
  sourceKeys.fanart='test-key';sourcePrefs.fanart=true;
  tmdb=async path=>new Promise((resolve,reject)=>pendingGallery.push({path,resolve,reject}));
  window.fetch=async url=>new Promise((resolve,reject)=>pendingFanart.push({url,resolve,reject}));
  state.media={media_type:'movie',id:101};
 }''')
 page.evaluate('()=>{loadFanartGallery()}')
 page.wait_for_function('pendingGallery.length===1')
 page.evaluate("document.getElementById('galleryType').value='backdrops';document.getElementById('galleryType').dispatchEvent(new Event('change'))")
 page.wait_for_function('pendingGallery.length===2')
 page.evaluate("pendingGallery[0].resolve({imdb_id:'tt0000101'})")
 page.wait_for_timeout(100)
 assert page.evaluate('pendingFanart.length')==0, 'Stale external ID must not trigger Fanart request'
 print('PASS: stale Fanart external-ID lookup stops before network request')
 page.evaluate("pendingGallery[1].resolve({backdrops:[]})")
 page.evaluate("document.getElementById('galleryType').value='posters'")
 page.evaluate('()=>{loadFanartGallery()}')
 page.wait_for_function('pendingGallery.length===3')
 page.evaluate("pendingGallery[2].resolve({imdb_id:'tt0000101'})")
 page.wait_for_function('pendingFanart.length===1')
 page.evaluate('''pendingFanart[0].resolve({ok:true,json:async()=>({movieposter:[
  {url:'javascript:alert(1)',lang:'en'},
  {url:'http://example.com/insecure.jpg',lang:'en'},
  {url:'https://example.com/safe.jpg',lang:'en'}]})})''')
 page.wait_for_function("document.getElementById('galleryCount').textContent.includes('1 Fanart.tv posters')")
 assert page.locator('#gallery img').count()==1
 assert page.locator('#gallery img').first.get_attribute('src')=='https://example.com/safe.jpg'
 print('PASS: Fanart artwork accepts HTTPS URLs and excludes unsafe protocols')
 browser.close()
