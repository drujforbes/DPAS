from pathlib import Path
from playwright.sync_api import sync_playwright
with sync_playwright() as pw:
 browser=pw.chromium.launch(headless=True,executable_path=__import__('os').environ.get('DPAS_CHROMIUM_PATH') or ('/usr/bin/chromium' if __import__('os').path.isfile('/usr/bin/chromium') else None),args=['--no-sandbox'])
 page=browser.new_page()
 page.set_content((Path(__file__).parent/'index.html').read_text(),wait_until='load')
 page.evaluate('''()=>{
  window.pendingGallery=[];
  tmdb=async path=>new Promise((resolve,reject)=>pendingGallery.push({path,resolve,reject}));
  state.media={media_type:'movie',id:101};
 }''')
 page.evaluate('()=>{loadGallery()}')
 page.wait_for_function('pendingGallery.length===1')
 page.evaluate("document.getElementById('galleryType').value='backdrops';document.getElementById('galleryType').dispatchEvent(new Event('change'))")
 page.wait_for_function('pendingGallery.length===2')
 page.evaluate("pendingGallery[1].resolve({backdrops:[{file_path:'/new.jpg',width:1920,height:1080,vote_count:1}]})")
 page.wait_for_function("document.getElementById('galleryCount').textContent.includes('1 backdrops')")
 page.evaluate("pendingGallery[0].resolve({posters:[{file_path:'/old.jpg',width:1000,height:1500,vote_count:1}]})")
 page.wait_for_timeout(150)
 assert page.locator('#gallery img').count()==1
 assert '/new.jpg' in page.locator('#gallery img').first.get_attribute('src')
 print('PASS: outdated TMDB poster reply cannot overwrite newer backdrop gallery')
 page.evaluate('()=>{loadGallery()}')
 page.wait_for_function('pendingGallery.length===3')
 page.evaluate("()=>{state.media={media_type:'movie',id:202};loadGallery()}")
 page.wait_for_function('pendingGallery.length===4')
 page.evaluate("pendingGallery[3].resolve({backdrops:[{file_path:'/title202.jpg',width:1920,height:1080}]})")
 page.wait_for_function("document.querySelector('#gallery img')?.src.includes('title202.jpg')")
 page.evaluate("pendingGallery[2].reject(new Error('Old title request failed'))")
 page.wait_for_timeout(150)
 assert 'title202.jpg' in page.locator('#gallery img').first.get_attribute('src')
 assert 'failed' not in page.locator('#galleryCount').inner_text()
 print('PASS: outdated title request error cannot replace new title gallery')
 browser.close()
