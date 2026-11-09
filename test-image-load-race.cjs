const fs=require('fs'),vm=require('vm'),assert=require('assert');
const html=fs.readFileSync(__dirname+'/index.html','utf8');
const match=html.match(/let imageLoadRequest=0;async function setImage\(src\)\{.*?\}\}async function selectLogo/);
assert(match,'image load guard not found');
const src=match[0].replace('async function selectLogo','');
let resolvers={};const state={mask:[]};const ctx={state,readImage:(key)=>new Promise(resolve=>resolvers[key]=resolve),draw:()=>{},status:()=>{}};
vm.createContext(ctx);vm.runInContext(src+';globalThis.setImage=setImage;globalThis.invalidate=()=>++imageLoadRequest;',ctx);
(async()=>{
 const old=ctx.setImage('old');const newest=ctx.setImage('new');resolvers.new({});await newest;resolvers.old({});await old;
 assert.equal(state.imageData,'new');console.log('PASS: stale image cannot replace newer artwork');
 const another=ctx.setImage('another');ctx.invalidate();resolvers.another({});await another;
 assert.equal(state.imageData,'new');console.log('PASS: title switch invalidates pending image');
 assert(html.includes('++galleryRequest;++imageLoadRequest;galleryItems=[]'),'title switch must invalidate images');
})().catch(e=>{console.error(e);process.exitCode=1});
