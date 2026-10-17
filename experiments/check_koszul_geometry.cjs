// Optional presentation QA: install Playwright and its Chromium browser first.
// Set HODGE_BROWSER_CHANNEL=msedge to use an installed Edge browser instead.
const {chromium}=require('playwright');
const path=require('path'),fs=require('fs'),crypto=require('crypto');
const {pathToFileURL}=require('url');
const ROOT=path.resolve(__dirname,'..'),OUT=path.join(ROOT,'results/koszul-geometry');
function insist(value,message){if(!value)throw Error(message);}
(async()=>{
  const browser=await chromium.launch({headless:true,...(process.env.HODGE_BROWSER_CHANNEL?{channel:process.env.HODGE_BROWSER_CHANNEL}:{})});
  const page=await browser.newPage({viewport:{width:768,height:850}}),errors=[];
  page.on('pageerror',e=>errors.push(e.message));
  await page.goto(pathToFileURL(path.join(ROOT,'visualizations/koszul-geometry-standalone.html')).href);
  const frame=page.frames().find(f=>f!==page.mainFrame());
  await frame.waitForSelector('[data-scene] circle');
  const snapshot=()=>frame.evaluate(()=>document.getElementById('koszul-geometric-map').geometrySnapshot());
  const layout=()=>frame.evaluate(()=>{
    const root=document.getElementById('koszul-geometric-map');
    const text=Array.from(root.querySelectorAll('svg text')).map(e=>{const r=e.getBoundingClientRect();return {label:e.textContent,x:r.x,y:r.y,w:r.width,h:r.height};});
    const collisions=[];
    for(let i=0;i<text.length;i++)for(let j=i+1;j<text.length;j++){
      const a=text[i],b=text[j];
      if(a.x<b.x+b.w+4&&a.x+a.w+4>b.x&&a.y<b.y+b.h+4&&a.y+a.h+4>b.y)collisions.push([a.label,b.label]);
    }
    return {overflow:document.documentElement.scrollWidth>innerWidth+1,collisions};
  });
  await page.waitForTimeout(300);
  await page.screenshot({path:path.join(OUT,'browser-light.png'),fullPage:true});
  const start=await snapshot();
  await frame.locator('[data-angle]').fill('120');await frame.locator('[data-angle]').dispatchEvent('input');await frame.locator('[data-angle]').dispatchEvent('change');
  await page.waitForTimeout(300);
  const moved=await snapshot();insist(Math.abs(start.image[0]-moved.image[0])>.1,'Probe did not move');
  const layouts=[];
  for(const contentWidth of [736,360,320]){
    await page.setViewportSize({width:contentWidth+32,height:1050});
    for(const family of ['1','2','4']){
      await frame.locator('[data-case]').selectOption(family);
      for(const fitted of [false,true]){
        if((await snapshot()).fitted!==fitted)await frame.locator('[data-fit]').click();
        for(const yaw of [-24,16,76,136,196,256,316]){
          await frame.evaluate(({family,yaw,fitted})=>window.dispatchEvent(new CustomEvent('openai:set_globals',{detail:{globals:{widgetState:{modelContent:{family:Number(family),angle:120,yaw,fitted}}}}})),{family,yaw,fitted});
          const s=await snapshot();
          insist(s.family===Number(family)&&s.fitted===fitted,'Requested state was not restored');
          insist(s.image[2]===0&&s.target[2]===1&&s.gap===1,'Exact display invariant changed');
          if(fitted)insist(Math.hypot(s.target[0]-s.image[0],s.target[1]-s.image[1])<1e-12,'Projected fit failed');
          layouts.push({width:contentWidth,family,fitted,yaw,...await layout()});
        }
      }
    }
  }
  await page.emulateMedia({colorScheme:'dark'});
  await frame.evaluate(()=>window.dispatchEvent(new CustomEvent('openai:set_globals',{detail:{globals:{widgetState:{modelContent:{family:4,angle:35,yaw:-24,fitted:true}}}}})));
  await page.screenshot({path:path.join(OUT,'browser-mobile.png'),fullPage:true});
  await page.setViewportSize({width:768,height:850});await page.waitForTimeout(300);
  await page.screenshot({path:path.join(OUT,'browser-dark.png'),fullPage:true});
  const beforeTurn=(await snapshot()).yaw;
  await frame.locator('[data-turn="1"]').click();await page.waitForTimeout(300);
  const afterTurn=(await snapshot()).yaw;
  insist(Math.abs((afterTurn-beforeTurn-20)%360)<1e-9,`Turn control failed: ${beforeTurn} -> ${afterTurn}`);
  const bad=layouts.filter(v=>v.overflow||v.collisions.length);
  const result={status:errors.length||bad.length?'FAIL':'PASS',browser:browser.version(),
    layoutsChecked:layouts.length,contentWidths:[736,360,320],scriptErrors:errors,layoutFailures:bad,
    interactions:['probe angle','denominator selection','projected fit','rotation','state restoration'],
    sourceFragmentSha256:crypto.createHash('sha256').update(fs.readFileSync(path.join(ROOT,'visualizations/koszul-geometry.html'),'utf8').replace(/\r\n/g,'\n')).digest('hex'),
    scope:'Presentation and displayed-map invariants; exact reconstruction is checked separately.'};
  fs.writeFileSync(path.join(OUT,'browser-validation.json'),JSON.stringify(result,null,2)+'\n');
  console.log(JSON.stringify(result,null,2));await browser.close();insist(result.status==='PASS','Browser checks failed');
})().catch(e=>{console.error(e);process.exit(1);});
