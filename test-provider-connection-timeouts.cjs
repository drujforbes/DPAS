const fs=require('fs'),assert=require('assert');
const s=fs.readFileSync(__dirname+'/index.html','utf8');
assert(s.includes("await providerFetch('https://api.themoviedb.org/3/configuration'"));
assert(s.includes("await providerFetch('https://webservice.fanart.tv/v3/movies/550?api_key='"));
assert(s.includes('const controller=new AbortController(),timer=setTimeout(()=>controller.abort(),timeoutMs)'));
console.log('PASS: both provider connection checks use bounded providerFetch');
