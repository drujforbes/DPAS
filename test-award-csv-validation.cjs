const assert=require('node:assert/strict');
function valid(type,outcome,source,year,category,recipient){let validSource=false;try{const u=new URL(source);validSource=['https:','http:'].includes(u.protocol)&&!!u.hostname}catch(_){};return !!(type&&outcome&&validSource&&/^\d{4}$/.test(year)&&Number(year)>=1900&&Number(year)<=2100&&category&&category.length<=160&&recipient&&recipient.length<=160)}
assert(valid('OSCAR','winner','https://www.oscars.org/','2025','Best Picture','A Film'));
for(const args of [['OSCAR','winner','https://example.org','','Best Picture','A Film'],['OSCAR','winner','javascript:alert(1)','2025','Best Picture','A Film'],['OSCAR','winner','https://example.org','2025','','A Film'],['OSCAR','winner','https://example.org','2025','Best Picture',''],['OSCAR','winner','https://example.org','1800','Best Picture','A Film']])assert(!valid(...args));
console.log('PASS: 6 award CSV validation cases');
