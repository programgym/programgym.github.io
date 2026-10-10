// Real-browser regression: rail navigation must never scroll the outer page.
const assert = require('assert/strict');
const playwright = require(process.env.PLAYWRIGHT_MODULE || 'playwright');
const engine = process.env.BROWSER_TYPE || 'chromium';
const baseURL = process.env.BASE_URL || 'http://127.0.0.1:8000/';
(async () => {
  const browser = await playwright[engine].launch({headless: true,
    ...(engine === 'chromium' ? {executablePath: process.env.CHROMIUM_EXECUTABLE || undefined, args: ['--no-sandbox']} : {})});
  const errors = [];
  for (const width of [390, 1440]) {
    const page = await browser.newPage({viewport: {width, height: 900}, hasTouch: width < 760,
      isMobile: width < 760, reducedMotion: 'reduce'});
    page.on('pageerror', e => errors.push(e.message));
    await page.route('https://fonts.googleapis.com/**', r => r.abort());
    await page.goto(baseURL + '#pipeline');
    for (const id of ['pipeFrame', 'agentFrame']) {
      const frame = await page.locator('#' + id).elementHandle().then(e => e.contentFrame());
      const down = frame.locator('#steps-down'), up = frame.locator('#steps-up');
      await down.scrollIntoViewIfNeeded();
      await frame.evaluate(() => document.getElementById('steps').scrollTo(0, 0));
      await page.waitForTimeout(100);
      const position = () => frame.locator('#steps').evaluate(e => e.scrollTop);
      const outer = await page.evaluate(() => scrollY);
      assert.equal(await up.getAttribute('aria-disabled'), 'true');
      assert.equal(await down.getAttribute('aria-disabled'), 'false');
      if (width < 760) await down.tap(); else await down.click();
      const first = await position();
      assert(first > 0, `${id}: down button should scroll the list`);
      await page.keyboard.press('s');
      assert(await position() > first, `${id}: S should scroll down in focused frame`);
      await page.keyboard.press('Shift+W');
      assert(Math.abs(await position() - first) <= 2, `${id}: W should scroll back up`);
      assert(Math.abs(await page.evaluate(() => scrollY) - outer) <= 1, `${id}: rail controls moved the host page`);
      // Space activates the focused scroll button rather than toggling playback.
      await page.keyboard.press('Space');
      assert(await position() > first);
      assert.equal(await frame.locator('#play').getAttribute('aria-pressed'), 'false');
      for (let n = 0; n < 60 && await down.getAttribute('aria-disabled') !== 'true'; n++) { await down.click(); await page.waitForTimeout(40); }
      assert.equal(await down.getAttribute('aria-disabled'), 'true', `${id}: all steps must be reachable`);
      const last = frame.locator('.beat').last();
      await last.click();
      assert.equal(await last.getAttribute('data-state'), 'now');
      for (let n = 0; n < 60 && await up.getAttribute('aria-disabled') !== 'true'; n++) { await up.click(); await page.waitForTimeout(40); }
      assert.equal(await up.getAttribute('aria-disabled'), 'true');
      // Native navigation and modified shortcuts must remain unclaimed.
      assert.deepEqual(await frame.evaluate(() => {
        return ['ArrowUp', 'ArrowDown', 's', 'w', 's'].map((key, i) => {
          const e = new KeyboardEvent('keydown', {key, bubbles: true, cancelable: true,
            ctrlKey: i === 2, metaKey: i === 3, altKey: i === 4});
          document.getElementById('steps-down').dispatchEvent(e);
          return e.defaultPrevented;
        });
      }), [false, false, false, false, false]);
      const beforeInput = await position();
      assert.equal(await frame.evaluate(() => {
        const input = document.createElement('input'); document.body.appendChild(input);
        const e = new KeyboardEvent('keydown', {key: 's', bubbles: true, cancelable: true});
        input.dispatchEvent(e); input.remove(); return e.defaultPrevented;
      }), false);
      assert.equal(await position(), beforeInput);
      // Once focus leaves the frame, W/S must not operate it.
      await page.evaluate(() => document.getElementById('themeBtn').focus({preventScroll: true}));
      await page.keyboard.press('s'); assert.equal(await position(), beforeInput);
      // An actual wheel gesture over the embedded list still scrolls the page.
      const box = await down.boundingBox();
      await page.mouse.move(box.x - 50, box.y + box.height + 25);
      const beforeWheel = await page.evaluate(() => scrollY);
      await page.mouse.wheel(0, 160); await page.waitForTimeout(350);
      assert(await page.evaluate(() => scrollY) > beforeWheel, `${id}: wheel over the list must scroll the host`);
      assert.equal(await position(), beforeInput, `${id}: wheel must not be stolen by the list`);
      console.log('PASS', engine, width, id, 'buttons / W,S / all rows / native keys and wheel');
    }
    await page.close();
  }
  assert.deepEqual(errors, []);
  await browser.close();
})().catch(e => { console.error(e); process.exit(1); });
