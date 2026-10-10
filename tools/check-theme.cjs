// Check real view-transition frames, not just the final data-theme attribute.
const assert = require('assert/strict');
const {chromium} = require(process.env.PLAYWRIGHT_MODULE || 'playwright');
const baseURL = process.env.BASE_URL || 'http://127.0.0.1:8000/';
(async () => {
  const browser = await chromium.launch({headless: true, executablePath: process.env.CHROMIUM_EXECUTABLE || undefined, args: ['--no-sandbox']});
  const errors = [];
  for (const width of [390, 1440]) {
    const page = await browser.newPage({viewport: {width, height: 900}, isMobile: width < 760, hasTouch: width < 760});
    page.on('pageerror', e => errors.push(e.message));
    await page.route('https://fonts.googleapis.com/**', r => r.abort());
    await page.addInitScript(() => {
      localStorage.setItem('theme', 'light');
      window.themeTransitions = [];
      const start = document.startViewTransition.bind(document);
      document.startViewTransition = function (update) {
        const transition = start(update);
        const record = {done: false, samples: []};
        window.themeTransitions.push(record);
        window.activeThemeTransition = transition;
        transition.finished.then(() => { record.done = true; }, () => { record.done = true; });
        transition.ready.then(() => {
          function sample() {
            if (record.done) return;
            record.samples.push(['old', 'new'].map(layer => getComputedStyle(document.documentElement, `::view-transition-${layer}(root)`).animationName));
            requestAnimationFrame(sample);
          }
          sample();
        }, () => {});
        return transition;
      };
    });
    await page.goto(baseURL + '#agent');
    await page.locator('#agentFrame').scrollIntoViewIfNeeded();
    await page.waitForTimeout(1000);
    const settle = async (theme, count) => {
      await page.waitForFunction(n => window.themeTransitions.length === n && window.themeTransitions.every(t => t.done), count);
      assert.equal(await page.locator('html').getAttribute('data-theme'), theme);
      assert.equal(await page.locator('#themeBtn').textContent(), theme === 'dark' ? 'Light' : 'Dark');
      assert.equal(await page.evaluate(() => localStorage.getItem('theme')), theme);
      assert.equal(await page.locator('html').evaluate(e => e.classList.contains('vt-theme')), false);
      for (const id of ['pipeFrame', 'agentFrame']) {
        const frame = await page.locator('#' + id).elementHandle().then(e => e.contentFrame());
        await frame.waitForFunction(t => document.documentElement.dataset.theme === t, theme);
      }
    };
    for (const [i, theme] of ['dark', 'light'].entries()) {
      await page.locator('#themeBtn').click();
      await settle(theme, i + 1);
    }
    const records = await page.evaluate(() => window.themeTransitions);
    for (const record of records) {
      assert(record.samples.length > 2, 'The reveal animation must run');
      for (const sample of record.samples) assert.deepEqual(sample, ['none', 'none'], 'A default cross-fade restarted before the snapshots were removed');
    }
    // Several clicks during one transition must not start competing snapshots.
    await page.evaluate(() => { for (let i = 0; i < 4; i++) document.getElementById('themeBtn').click(); });
    await settle('dark', 3);
    // A skipped transition still applies the theme and releases the next click.
    await page.evaluate(() => { document.getElementById('themeBtn').click(); window.activeThemeTransition.skipTransition(); });
    await settle('light', 4);
    await page.locator('#themeBtn').click();
    await settle('dark', 5);
    console.log('PASS theme animation / both directions / repeated clicks / cancellation / iframe sync', width);
    await page.close();
  }
  for (const fallback of ['reduced-motion', 'no-view-transition']) {
    const page = await browser.newPage({reducedMotion: fallback === 'reduced-motion' ? 'reduce' : 'no-preference'});
    page.on('pageerror', e => errors.push(e.message));
    await page.route('https://fonts.googleapis.com/**', r => r.abort());
    await page.addInitScript(mode => { localStorage.setItem('theme', 'light'); if (mode === 'no-view-transition') document.startViewTransition = undefined; }, fallback);
    await page.goto(baseURL);
    for (const theme of ['dark', 'light']) {
      await page.locator('#themeBtn').click();
      assert.equal(await page.locator('html').getAttribute('data-theme'), theme);
      assert.equal(await page.locator('html').evaluate(e => e.classList.contains('vt-theme')), false);
    }
    console.log('PASS theme fallback', fallback);
    await page.close();
  }
  assert.deepEqual(errors, []);
  await browser.close();
})().catch(e => { console.error(e); process.exit(1); });
