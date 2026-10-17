// Presentation QA with Playwright; HODGE_BROWSER_CHANNEL=msedge is supported.
const {chromium}=require('playwright');
const fs=require('fs'),path=require('path'),crypto=require('crypto');
const {pathToFileURL}=require('url');
const ROOT=path.resolve(__dirname,'..'),OUT=path.join(ROOT,'results/koszul-map-sweep');
const assert=(b,m)=>{if(!b)throw Error(m);};
(async()=>{
 const browser=await chromium.launch({headless:true,...(process.env.HODGE_BROWSER_CHANNEL?{channel:process.env.HODGE_BROWSER_CHANNEL}:{})});
 const page=await browser.newPage({viewport:{width:768,height:1100}}),errors=[];
 page.on('pageerror',e=>errors.push(e.message));
 await page.goto(pathToFileURL(path.join(ROOT,'visualizations/koszul-map-sweep-standalone.html')).href);
 const f=page.frames().find(p=>p!==page.mainFrame());await f.waitForSelector('[data-chart] rect');
 const snapshot=()=>f.evaluate(()=>document.getElementById('koszul-denominator-sweep').sweepSnapshot());
 const set=state=>f.evaluate(v=>window.dispatchEvent(new CustomEvent('openai:set_globals',{detail:{globals:{widgetState:{modelContent:v}}}})),state);
 const layouts=[];
 for(const width of [736,360,320]){
  await page.setViewportSize({width:width+32,height:1250});
  for(const frame of [0,1])for(const kind of ['rank','spectrum'])for(const [s,t] of [[0,0],[0,1],[1,0],[1,1],[-2,2],[2,-2]]){
   await set({s,t,frame,kind});const p=await snapshot();
   assert(p.fullRank===(s?720:t?713:690),'Incorrect full rank');assert(p.target[2]===1,'Changed exact obstruction');
   if(frame===1)assert(p.projectionRank===(s!==0)+(t!==0),'Incorrect sensitive projection rank');
   const bounds=await f.evaluate(()=>{
    const root=document.getElementById('koszul-denominator-sweep');
    const labels=[...root.querySelectorAll('svg text')].filter(e=>e.getBoundingClientRect().width).map(e=>{const r=e.getBoundingClientRect();return {text:e.textContent,x:r.x,y:r.y,w:r.width,h:r.height};});
    const overlaps=[];
    for(let i=0;i<labels.length;i++)for(let j=i+1;j<labels.length;j++){
      const a=labels[i],b=labels[j];if(a.x<b.x+b.w+4&&a.x+a.w+4>b.x&&a.y<b.y+b.h+4&&a.y+a.h+4>b.y)overlaps.push([a.text,b.text]);
    }
    return {overflow:document.documentElement.scrollWidth>innerWidth+1,overlaps};
   });
   layouts.push({width,frame,kind,s,t,...bounds});
  }
 }
 await set({s:1,t:1,frame:1,kind:'rank'});
 await f.locator('[data-s]').fill('0');await f.locator('[data-s]').dispatchEvent('input');await f.locator('[data-s]').dispatchEvent('change');
 await page.waitForTimeout(250);assert((await snapshot()).fullRank===713,'Slider did not change map');
 await f.locator('[data-frame]').selectOption('0');assert((await snapshot()).frame===0,'Frame selector failed');
 await f.locator('[data-chart-kind="spectrum"]').click();assert((await snapshot()).kind==='spectrum','Spectrum tab failed');
 const overlay=f.locator('[data-chart-hit]');await overlay.hover({position:{x:75,y:80}});assert(await f.locator('[data-tooltip-box]').isVisible(),'Tooltip missing');
 await set({s:1,t:1,frame:1,kind:'rank'});
 const hit=await f.locator('[data-chart-hit]').boundingBox();await page.mouse.click(hit.x+hit.width/2,hit.y+hit.height/2);
 await page.waitForTimeout(250);assert((await snapshot()).fullRank===690,'Grid selection failed');
 await page.emulateMedia({colorScheme:'dark'});await page.screenshot({path:path.join(OUT,'browser-mobile.png'),fullPage:true});
 await page.setViewportSize({width:768,height:1100});await set({s:1,t:0,frame:1,kind:'rank'});await page.waitForTimeout(200);
 await page.screenshot({path:path.join(OUT,'browser-dark.png'),fullPage:true});
 await page.emulateMedia({colorScheme:'light'});await set({s:1,t:1,frame:1,kind:'rank'});await page.waitForTimeout(200);
 await page.screenshot({path:path.join(OUT,'browser-light.png'),fullPage:true});
 const bad=layouts.filter(v=>v.overflow||v.overlaps.length);
 const report={status:errors.length||bad.length?'FAIL':'PASS',browser:browser.version(),layouts:layouts.length,widths:[736,360,320],errors,layoutFailures:bad,
   interactions:['coefficient sliders','projection selection','rank/spectrum tabs','grid selection','tooltip','state restoration'],
   fragmentSha256:crypto.createHash('sha256').update(fs.readFileSync(path.join(ROOT,'visualizations/koszul-map-sweep.html'),'utf8').replace(/\r\n/g,'\n')).digest('hex')};
 fs.writeFileSync(path.join(OUT,'browser-validation.json'),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report,null,2));await browser.close();assert(report.status==='PASS','Presentation QA failed');
})().catch(e=>{console.error(e);process.exit(1);});
