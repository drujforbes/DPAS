const assert=require('node:assert/strict');
const fs=require('node:fs');const vm=require('node:vm');const path=require('node:path');
const html=fs.readFileSync(path.join(__dirname,'index.html'),'utf8');
const start=html.indexOf('function validatePASProject(p){');
const end=html.indexOf("$('projectFile').onchange=",start);
assert.ok(start>=0&&end>start,'validator must exist in HTML');
const validatePASProject=vm.runInNewContext(html.slice(start,end)+'\nvalidatePASProject');
const valid={version:1,format:'poster',title:'Example',awards:[{type:'OSCAR',outcome:'winner'}],logos:{},settings:{opacity:'0.5',cropFill:true}};
assert.equal(validatePASProject(valid),valid);
const cases=[
 ['bad version',{version:2}],['bad format',{format:'other'}],
 ['invalid image',{image:'https://example.com/a.png'}],
 ['invalid logo',{logos:{X:'javascript:alert(1)'}}],
 ['invalid award',{awards:[{type:'OTHER',outcome:'winner'}]}],
 ['array award',{awards:[['OSCAR','winner']]}],
 ['invalid selected logo',{selectedLogo:4}],
 ['oversized title',{title:'x'.repeat(501)}],
 ['bad setting',{settings:{opacity:'Infinity'}}],
 ['unknown setting',{settings:{unsafe:'unexpected'}}],
 ['prototype key',{logos:JSON.parse('{"__proto__":"data:image/png;base64,YQ=="}')}],
 ['constructor key',{logos:{constructor:'data:image/png;base64,YQ=='}}],
 ['award year invalid',{awards:[{type:'OSCAR',outcome:'winner',year:'tomorrow'}]}],
 ['award source invalid',{awards:[{type:'OSCAR',outcome:'winner',source:'javascript:alert(1)'}]}],
 ['award category type invalid',{awards:[{type:'EMMY',outcome:'nominee',category:{}}]}],
 ['award recipient too long',{awards:[{type:'SAG',outcome:'winner',recipient:'x'.repeat(501)}]}]
];
for(const [label,patch] of cases){assert.throws(()=>validatePASProject({...valid,...patch}),/invalid|unsupported|must|exceeds|Invalid|Unsupported/,label)}
console.log('PASS: '+(cases.length+1)+' tests against actual HTML validator');
