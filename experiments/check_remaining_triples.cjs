// Every displayed exact identity at three widths, plus controls and themes.
const {chromium}=require('playwright');
const fs=require('fs'),path=require('path'),crypto=require('crypto');
const {pathToFileURL}=require('url');
const ROOT=path.resolve(__dirname,'..'),OUT=path.join(ROOT,'results/remaining-triples-shared');
const assert=(c,m)=>{if(!c)throw Error(m);};
(async()=>{
 const data=JSON.parse(fs.readFileSync(path.join(OUT,'visual-data.json'),'utf8'));
 const browser=await chromium.launch({headless:true,...(process.env.HODGE_BROWSER_CHANNEL?{channel:process.env.HODGE_BROWSER_CHANNEL}:{})});
 const page=await browser.newPage({viewport:{width:768,height:1000}}),errors=[];
 page.on('pageerror',e=>errors.push(e.message));
 await page.goto(pathToFileURL(path.join(ROOT,'visualizations/remaining-triples-standalone.html')).href);
 const f=page.frames().find(f=>f!==page.mainFrame());await f.waitForSelector('[data-chart-frame]');
 const set=state=>f.evaluate(v=>window.dispatchEvent(new CustomEvent('openai:set_globals',{detail:{globals:{widgetState:{modelContent:v}}}})),state);
 const snapshot=()=>f.evaluate(()=>document.getElementById('remaining-triples').strandSnapshot());
 const failures=[];let layouts=0;
 for(const width of [736,360,320]){
  await page.setViewportSize({width:width+32,height:1100});
  for(const family of data.families)for(let block=0;block<family.blocks.length;block++){
   const s=family.blocks[block];
   for(let example=0;example<s.examples.length;example++){
    await set({family:family.number,block,example,monomial:-1});
    const p=await snapshot();assert(p.rank===s.rank&&p.kernel===s.kernel,'Wrong dimensions');
    assert(p.excluded===family.excluded&&p.zeros===s.zeros.length,'Wrong outcome');
    assert(p.sum===s.examples[example].sums[p.monomial],'Wrong exact sum');
    const checks=await f.evaluate(()=>{
     const root=document.getElementById('remaining-triples'),r=root.getBoundingClientRect();
     const labels=[...root.querySelectorAll('svg text')].map(e=>{const b=e.getBoundingClientRect();return {text:e.textContent,x:b.x,y:b.y,w:b.width,h:b.height};});
     const overlaps=[];
     for(let i=0;i<labels.length;i++)for(let j=i+1;j<labels.length;j++){
      const a=labels[i],b=labels[j];if(a.x<b.x+b.w+4&&a.x+a.w+4>b.x&&a.y<b.y+b.h+4&&a.y+a.h+4>b.y)overlaps.push([a.text,b.text]);
     }
     return {overflow:document.documentElement.scrollWidth>innerWidth+1,
       clipped:labels.filter(b=>b.x<r.left-1||b.x+b.w>r.right+1).map(b=>b.text),overlaps};
    });
    layouts++;if(checks.overflow||checks.clipped.length||checks.overlaps.length)failures.push({width,family:family.number,block,example,...checks});
   }
  }
 }
 await set({family:17,block:1,example:0,monomial:-1});
 assert((await snapshot()).zeros===5,'Degree-six powers missing');
 await f.locator('[data-block]').selectOption('0');
 assert((await snapshot()).zeros===0,'Failed pre-rebuild block mislabeled');
 await f.locator('[data-family]').selectOption('151');
 assert(!(await snapshot()).excluded,'Unresolved family mislabeled');
 assert((await snapshot()).sum!=='0','Linear-square example missing');
 await f.locator('[data-block]').selectOption('1');
 assert((await snapshot()).sum==='0','Koszul boundary failed');
 await set({family:17,block:1,example:0,monomial:-1});
 const ex=data.families[0].blocks[1].examples[0];
 await f.locator('[data-monomial]').selectOption(String(ex.sums.findIndex(s=>s==='0')));
 assert((await snapshot()).sum==='0','Cancellation selection failed');
 await page.waitForTimeout(200);
 await f.locator('[data-chart-hit]').first().click();assert(await f.locator('[data-tip]').isVisible(),'Missing tooltip');
 await set({family:17,block:1,example:0,monomial:-1});await page.waitForTimeout(300);
 await page.emulateMedia({colorScheme:'dark'});await page.screenshot({path:path.join(OUT,'browser-mobile.png'),fullPage:true});
 await page.setViewportSize({width:768,height:1000});await page.waitForTimeout(200);
 await page.screenshot({path:path.join(OUT,'browser-dark.png'),fullPage:true});
 await page.emulateMedia({colorScheme:'light'});await page.screenshot({path:path.join(OUT,'browser-light.png'),fullPage:true});
 const report={status:failures.length||errors.length?'FAIL':'PASS',browser:browser.version(),layouts,widths:[736,360,320],failures,errors,
   interactions:['family','before/after block','sixth power','Koszul boundary','linear square','monomial','tooltip','state restoration','failed power search'],
   fragmentSha256:crypto.createHash('sha256').update(fs.readFileSync(path.join(ROOT,'visualizations/remaining-triples.html'),'utf8').replace(/\r\n/g,'\n')).digest('hex')};
 fs.writeFileSync(path.join(OUT,'browser-validation.json'),JSON.stringify(report,null,2)+'\n');
 console.log(JSON.stringify(report,null,2));await browser.close();assert(report.status==='PASS','Presentation checks failed');
})().catch(e=>{console.error(e);process.exit(1);});
