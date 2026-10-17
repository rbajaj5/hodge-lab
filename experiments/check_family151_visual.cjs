const {chromium}=require('playwright');
const fs=require('fs'),path=require('path'),crypto=require('crypto');
const {pathToFileURL}=require('url');
const ROOT=path.resolve(__dirname,'..'),OUT=path.join(ROOT,'results/family151-multipliers');
const assert=(v,m)=>{if(!v)throw Error(m);};
(async()=>{
 const data=JSON.parse(fs.readFileSync(path.join(OUT,'visual-data.json'),'utf8'));
 const browser=await chromium.launch({headless:true,...(process.env.HODGE_BROWSER_CHANNEL?{channel:process.env.HODGE_BROWSER_CHANNEL}:{})});
 const page=await browser.newPage({viewport:{width:768,height:1100}}),errors=[];
 page.on('pageerror',e=>errors.push(e.message));
 await page.goto(pathToFileURL(path.join(ROOT,'visualizations/family151-multipliers-standalone.html')).href);
 const frame=page.frames().find(f=>f!==page.mainFrame());await frame.waitForSelector('[data-chart-frame]');
 const set=s=>frame.evaluate(v=>window.dispatchEvent(new CustomEvent('openai:set_globals',{detail:{globals:{widgetState:{modelContent:v}}}})),s);
 const snap=()=>frame.evaluate(()=>document.getElementById('family151-multipliers').multiplierSnapshot());
 let layouts=0;const failures=[];
 for(const width of [736,360,320]){
  await page.setViewportSize({width:width+32,height:1100});
  for(const c of data.cases)for(let example=0;example<c.examples.length;example++){
   const ex=c.examples[example],indices=[ex.defaultMonomial,ex.monomials.findIndex(m=>m.sum!=='0')];
   for(const monomial of indices){
    await set({case:c.key,example,monomial});const s=await snap();
    assert(s.newRelations===c.newRelations&&s.sum===ex.monomials[monomial].sum,'Wrong coefficient or count');
    assert(s.numerator===ex.monomials[monomial].numerator,'Wrong variable category');
    const checks=await frame.evaluate(()=>{
     const root=document.getElementById('family151-multipliers'),r=root.getBoundingClientRect();
     const labels=[...root.querySelectorAll('svg text')].map(e=>{const b=e.getBoundingClientRect();return {text:e.textContent,x:b.x,y:b.y,w:b.width,h:b.height};});
     const overlaps=[];
     for(let i=0;i<labels.length;i++)for(let j=i+1;j<labels.length;j++){
      const a=labels[i],b=labels[j];if(a.x<b.x+b.w+4&&a.x+a.w+4>b.x&&a.y<b.y+b.h+4&&a.y+a.h+4>b.y)overlaps.push([a.text,b.text]);
     }
     return {overflow:document.documentElement.scrollWidth>innerWidth+1,
      clipped:labels.filter(b=>b.x<r.left-1||b.x+b.w>r.right+1).map(b=>b.text),overlaps};
    });
    layouts++;if(checks.overflow||checks.clipped.length||checks.overlaps.length)failures.push({width,case:c.key,example,monomial,...checks});
   }
  }
 }
 await set({case:'global',example:0,monomial:-1});
 assert((await snap()).sum==='0','Numerator does not cancel');
 await frame.locator('[data-case]').selectOption('115');assert((await snap()).case==='115','Chart control failed');
 const ex=data.cases.find(c=>c.key==='115').examples[0];
 await frame.locator('[data-monomial]').selectOption(String(ex.monomials.findIndex(m=>m.sum!=='0')));
 assert((await snap()).sum!=='0','Denominator residue missing');
 await page.waitForTimeout(150);await frame.locator('[data-chart-hit]').first().click();
 assert(await frame.locator('[data-tip]').isVisible(),'Tooltip missing');
 await frame.locator('[data-case]').selectOption('global');await page.waitForTimeout(350);
 assert((await snap()).case==='global'&&(await snap()).sum==='0','Final control/state restoration failed');
 await page.emulateMedia({colorScheme:'dark'});await page.screenshot({path:path.join(OUT,'browser-mobile.png'),fullPage:true});
 await page.setViewportSize({width:768,height:1100});await page.waitForTimeout(150);
 await page.screenshot({path:path.join(OUT,'browser-dark.png'),fullPage:true});
 await page.emulateMedia({colorScheme:'light'});await page.screenshot({path:path.join(OUT,'browser-light.png'),fullPage:true});
 const report={status:errors.length||failures.length?'FAIL':'PASS',browser:browser.version(),layouts,widths:[736,360,320],errors,failures,
  interactions:['equation chart','relation','monomial','numerator cancellation','denominator residue','tooltip','state restoration'],
  fragmentSha256:crypto.createHash('sha256').update(fs.readFileSync(path.join(ROOT,'visualizations/family151-multipliers.html'),'utf8').replace(/\r\n/g,'\n')).digest('hex')};
 fs.writeFileSync(path.join(OUT,'browser-validation.json'),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report,null,2));
 await browser.close();assert(report.status==='PASS','Presentation checks failed');
})().catch(e=>{console.error(e);process.exit(1);});
