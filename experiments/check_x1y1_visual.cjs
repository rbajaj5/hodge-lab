const {chromium}=require('playwright');
const fs=require('fs'),path=require('path'),crypto=require('crypto');
const {pathToFileURL}=require('url');
const ROOT=path.resolve(__dirname,'..'),OUT=path.join(ROOT,'results/x1y1-extensions');
const assert=(v,m)=>{if(!v)throw Error(m);};
(async()=>{
 const data=JSON.parse(fs.readFileSync(path.join(OUT,'visual-data.json'),'utf8'));
 const browser=await chromium.launch({headless:true,...(process.env.HODGE_BROWSER_CHANNEL?{channel:process.env.HODGE_BROWSER_CHANNEL}:{})});
 const page=await browser.newPage({viewport:{width:768,height:850}}),errors=[];
 page.on('pageerror',e=>errors.push(e.message));
 await page.goto(pathToFileURL(path.join(ROOT,'visualizations/x1y1-extensions-standalone.html')).href);
 const frame=page.frames().find(f=>f!==page.mainFrame());await frame.waitForSelector('[data-chart-frame]');
 const set=s=>frame.evaluate(v=>window.dispatchEvent(new CustomEvent('openai:set_globals',{detail:{globals:{widgetState:{modelContent:v}}}})),s);
 const snap=()=>frame.evaluate(()=>document.getElementById('x1y1-extensions').mapSnapshot());
 let layouts=0;const failures=[];
 for(const width of [736,360,320]){
  await page.setViewportSize({width:width+32,height:850});
  for(const c of data.cases)for(const m of c.maps){
   await set({family:c.batch_number,degree:m.degree});const s=await snap();
   assert(s.rank===m.rank&&s.domain===m.domain&&s.codomain===m.codomain&&s.entries===m.cells.length,'Matrix state differs');
   const checks=await frame.evaluate(()=>{
    const root=document.getElementById('x1y1-extensions'),r=root.getBoundingClientRect();
    const labels=[...root.querySelectorAll('svg text')].map(e=>{const b=e.getBoundingClientRect();return {text:e.textContent,x:b.x,y:b.y,w:b.width,h:b.height};});
    const overlaps=[];
    for(let i=0;i<labels.length;i++)for(let j=i+1;j<labels.length;j++){
     const a=labels[i],b=labels[j];if(a.x<b.x+b.w+4&&a.x+a.w+4>b.x&&a.y<b.y+b.h+4&&a.y+a.h+4>b.y)overlaps.push([a.text,b.text]);
    }
    return {overflow:document.documentElement.scrollWidth>innerWidth+1,
     clipped:labels.filter(b=>b.x<r.left-1||b.x+b.w>r.right+1).map(b=>b.text),overlaps};
   });
   layouts++;if(checks.overflow||checks.clipped.length||checks.overlaps.length)failures.push({width,family:c.batch_number,degree:m.degree,...checks});
  }
 }
 await frame.locator('[data-family]').selectOption('19');await frame.locator('[data-degree]').selectOption('4');
 assert((await snap()).rank===24,'Native controls failed');
 await frame.locator('[data-chart-hit]').click();assert(await frame.locator('[data-tip]').isVisible(),'Tooltip missing');
 await set({family:75,degree:3});assert((await snap()).domain===0,'Empty map wrong');
 await set({family:19,degree:4});await page.emulateMedia({colorScheme:'dark'});
 await page.screenshot({path:path.join(OUT,'browser-mobile.png'),fullPage:true});
 await page.setViewportSize({width:768,height:850});await page.waitForTimeout(200);
 await page.screenshot({path:path.join(OUT,'browser-dark.png'),fullPage:true});
 await page.emulateMedia({colorScheme:'light'});await page.screenshot({path:path.join(OUT,'browser-light.png'),fullPage:true});
 const report={status:errors.length||failures.length?'FAIL':'PASS',browser:browser.version(),layouts,widths:[736,360,320],errors,failures,
  interactions:['family','degree','exact entry tooltip','empty map','state restoration'],
  fragmentSha256:crypto.createHash('sha256').update(fs.readFileSync(path.join(ROOT,'visualizations/x1y1-extensions.html'),'utf8').replace(/\r\n/g,'\n')).digest('hex')};
 fs.writeFileSync(path.join(OUT,'browser-validation.json'),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report,null,2));
 await browser.close();assert(report.status==='PASS','Presentation checks failed');
})().catch(e=>{console.error(e);process.exit(1);});
