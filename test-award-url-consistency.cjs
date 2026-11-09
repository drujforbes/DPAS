const fs=require('node:fs');
const vm=require('node:vm');
const assert=require('node:assert/strict');
const html=fs.readFileSync(__dirname+'/index.html','utf8');
const start=html.indexOf('function pasValidEvidenceURL(');
const end=html.indexOf('function pasParseCSV(',start);
assert(start>=0&&end>start,'Validator missing');
const context={URL};
vm.runInNewContext(html.slice(start,end),context);
const cases=[
 ['https://www.oscars.org/oscars/ceremonies/2025',true],
 ['http://example.org/award',true],
 ['https://user:pass@example.org/award',false],
 ['javascript:alert(1)',false],
 ['file:///tmp/award',false],
 ['not-a-url',false],
 ['',false],
 ['https://example.org',true],
];
for(const [url,expected] of cases)assert.equal(context.pasValidEvidenceURL(url),expected,url);
assert(html.includes("['award','outcome','year','category','recipient','source'].some(k=>col(k)<0)"),'Required CSV columns must be checked');
console.log('PASS: 8 award evidence URL cases + required CSV header check');
