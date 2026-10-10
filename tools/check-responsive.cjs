// Run against the local preview with Playwright installed (see README).
const {chromium}=require(process.env.PLAYWRIGHT_MODULE || 'playwright');
const baseURL=process.env.BASE_URL || 'http://127.0.0.1:8000/';
const assert=require('assert/strict');
(async()=>{
 const browser=await chromium.launch({headless:true,executablePath:process.env.CHROMIUM_EXECUTABLE || undefined,args:['--no-sandbox']});
 const errors=[];
 for(const width of [320,375,390,430,760,768,1024,1280,1440,1920]) {
  const mobile=width<=760;
  const page=await browser.newPage({viewport:{width,height:900},hasTouch:mobile,isMobile:mobile,deviceScaleFactor:1,reducedMotion:'reduce'});
  page.on('pageerror',e=>errors.push(`${width}: ${e.message}`));
  await page.route('https://fonts.googleapis.com/**',r=>r.abort());
  await page.goto(baseURL,{waitUntil:'load'});
  for(const theme of ['light','dark']){
   await page.evaluate(theme=>document.documentElement.dataset.theme=theme,theme);
   await page.waitForTimeout(50);
   const layout=await page.evaluate(()=>({width:innerWidth,scroll:document.documentElement.scrollWidth,panels:[...document.querySelectorAll('.vpanel')].map(e=>({id:e.id,x:e.getBoundingClientRect().x,right:e.getBoundingClientRect().right,width:e.getBoundingClientRect().width}))}));
   assert(layout.scroll<=width+1,`${width}/${theme}: page width ${layout.scroll}`);
   if(mobile)for(const panel of layout.panels){assert(Math.abs(panel.width-(width-32))<1,`${width}/${theme}: unequal ${panel.id} ${panel.width}`);}
   for(const id of ['pipeFrame','agentFrame']){
    const el=page.locator('#'+id); await el.scrollIntoViewIfNeeded();
    const frame=await el.elementHandle().then(e=>e.contentFrame()); await frame.waitForSelector('#fig');
    const geometry=await frame.evaluate(()=>{const rect=s=>{let r=document.querySelector(s).getBoundingClientRect();return{x:r.x,right:r.right,y:r.y,bottom:r.bottom,width:r.width,height:r.height}};return{width:innerWidth,scroll:document.documentElement.scrollWidth,label:rect('.sheetlabel'),fig:rect('#fig'),buttons:[...document.querySelectorAll('.transport .btn')].map(e=>({id:e.id,right:e.getBoundingClientRect().right,bottom:e.getBoundingClientRect().bottom})),transport:rect('.transport'),theme:document.documentElement.dataset.theme};});
    assert(geometry.scroll<=geometry.width+1,`${width}/${theme}/${id}: frame overflow ${JSON.stringify(geometry)}`);
    assert.equal(geometry.theme,theme);
    if(geometry.width<=880){assert(geometry.label.bottom<=geometry.fig.y+1,`${width}/${id}: caption overlap`);assert(geometry.fig.height>80,`${width}/${id}: figure too short`);}
    for(const button of geometry.buttons){assert(button.right<=geometry.width+1,`${width}/${id}: clipped ${button.id}`);assert(button.bottom<=geometry.transport.bottom+1,`${width}/${id}: button below transport`);}
    await frame.locator('#next').click(); await frame.locator('#showall').click();
   }
  }
  console.log('PASS layout/light/dark/frames',width);
  if([390,1440].includes(width)){
   const hit=page.locator('.actp .hit').first(); await hit.scrollIntoViewIfNeeded(); await page.waitForTimeout(150);
   const box=await hit.boundingBox(); const x=box.x+box.width*.6,y=Math.max(70,box.y+box.height*.5);
   const open=async()=>{if(mobile)await page.touchscreen.tap(x,y);else {await page.mouse.move(0,60);await page.waitForTimeout(200);await page.mouse.move(x,y);} await page.waitForTimeout(120);assert(await page.locator('#tip').evaluate(e=>e.classList.contains('on')),'tip should open');};
   const closed=async()=>{await page.waitForTimeout(180);assert(!await page.locator('#tip').evaluate(e=>e.classList.contains('on')),'tip should close');assert.equal(await page.locator('.actp .cur').first().evaluate(e=>e.style.display),'none');};
   await open();
   assert.match(await page.locator('#tip').textContent(),/Total/);assert.equal(await page.locator('#tip').evaluate(e=>getComputedStyle(e).visibility),'visible');
   const tipbox=await page.locator('#tip').boundingBox();assert(tipbox.x>=0&&tipbox.x+tipbox.width<=width&&tipbox.y>=0&&tipbox.y+tipbox.height<=900,'tip viewport bounds');
   await page.locator('.tip-close').click();await closed();
   await open();await page.keyboard.press('Escape');await closed();
   if(!mobile){await page.mouse.move(x+1,y+1);await closed();}
   await open();await page.mouse.click(5,80);await closed();
   await open();await page.evaluate(()=>window.scrollBy(0,60));await closed();
   await hit.scrollIntoViewIfNeeded();
   const updated=await hit.boundingBox();
   if(mobile){await page.touchscreen.tap(updated.x+updated.width*.6,updated.y+updated.height*.5);assert(await page.locator('#tip').evaluate(e=>e.classList.contains('on')));await page.touchscreen.tap(updated.x+updated.width*.6,updated.y+updated.height*.5);await closed();}
   else{await page.keyboard.press('Tab');await hit.focus();assert(await page.locator('#tip').evaluate(e=>e.classList.contains('on')));await page.keyboard.press('Escape');await closed();}
   console.log('PASS tooltips',width);
  }
  await page.close();
 }
 assert.deepEqual(errors,[]); console.log('PASS no browser script errors');
 await browser.close();
})().catch(e=>{console.error(e);process.exit(1)});
