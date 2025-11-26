const puppeteer = require('puppeteer');

const BASE_URL = 'http://localhost:3005';

const pages = [
  { name: 'Dashboard', path: '/' },
  { name: 'Organizations', path: '/organizations' },
  { name: 'Entities', path: '/entities' },
  { name: 'Software', path: '/software' },
  { name: 'Services', path: '/services' },
  { name: 'Data Stores', path: '/data-stores' },
  { name: 'Issues', path: '/issues' },
  { name: 'Labels', path: '/labels' },
  { name: 'Milestones', path: '/milestones' },
  { name: 'Projects', path: '/projects' },
  { name: 'Identity Center', path: '/iam' },
  { name: 'Keys', path: '/keys' },
  { name: 'Secrets', path: '/secrets' },
  { name: 'Certificates', path: '/certificates' },
  { name: 'Dependencies', path: '/dependencies' },
  { name: 'Discovery', path: '/discovery' },
  { name: 'Profile', path: '/profile' },
];

async function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

async function testPages() {
  const browser = await puppeteer.launch({
    headless: 'new',
    args: ['--no-sandbox', '--disable-setuid-sandbox'],
  });

  const page = await browser.newPage();
  await page.setViewport({ width: 1920, height: 1080 });

  const errors = [];
  const apiErrors = [];

  // Capture console errors
  page.on('console', msg => {
    if (msg.type() === 'error') {
      errors.push({ type: 'console', message: msg.text() });
    }
  });

  // Capture failed network requests
  page.on('requestfailed', request => {
    errors.push({ type: 'network', url: request.url(), failure: request.failure()?.errorText });
  });

  // Capture API responses
  page.on('response', response => {
    const url = response.url();
    const status = response.status();
    if (url.includes('/api/') && status >= 400) {
      apiErrors.push({ url, status });
    }
  });

  // Login first
  console.log('Logging in...');
  await page.goto(`${BASE_URL}/login`, { waitUntil: 'networkidle0', timeout: 60000 });
  await sleep(1000);

  const inputs = await page.$$('input');
  if (inputs.length >= 2) {
    await inputs[0].type('admin@localhost');
    await inputs[1].type('admin123');
  }

  await page.click('button[type="submit"]');

  try {
    await page.waitForFunction(
      () => !window.location.pathname.includes('/login'),
      { timeout: 30000 }
    );
  } catch (e) {
    console.log('Login navigation timeout');
  }
  await sleep(2000);
  console.log('Logged in, current URL:', page.url());
  console.log('');

  // Test each page
  const results = [];
  for (const pageInfo of pages) {
    errors.length = 0;
    apiErrors.length = 0;

    console.log(`Testing: ${pageInfo.name} (${pageInfo.path})...`);

    try {
      await page.goto(`${BASE_URL}${pageInfo.path}`, { waitUntil: 'networkidle0', timeout: 60000 });
      await sleep(2000);

      const currentUrl = page.url();
      if (currentUrl.includes('/login')) {
        console.log(`  REDIRECT: Redirected to login`);
        results.push({ page: pageInfo.name, status: 'REDIRECT', errors: [], apiErrors: [] });
        continue;
      }

      const pageErrors = [...errors];
      const pageApiErrors = [...apiErrors];

      if (pageErrors.length === 0 && pageApiErrors.length === 0) {
        console.log(`  OK: No errors`);
        results.push({ page: pageInfo.name, status: 'OK', errors: [], apiErrors: [] });
      } else {
        console.log(`  ERRORS: ${pageErrors.length} console, ${pageApiErrors.length} API`);
        if (pageErrors.length > 0) {
          pageErrors.forEach(e => console.log(`    - ${e.type}: ${e.message || e.url}`));
        }
        if (pageApiErrors.length > 0) {
          pageApiErrors.forEach(e => console.log(`    - API ${e.status}: ${e.url}`));
        }
        results.push({ page: pageInfo.name, status: 'ERRORS', errors: pageErrors, apiErrors: pageApiErrors });
      }
    } catch (error) {
      console.log(`  ERROR: ${error.message}`);
      results.push({ page: pageInfo.name, status: 'EXCEPTION', errors: [{ type: 'exception', message: error.message }], apiErrors: [] });
    }
  }

  await browser.close();

  // Summary
  console.log('');
  console.log('=== SUMMARY ===');
  const ok = results.filter(r => r.status === 'OK').length;
  const failed = results.filter(r => r.status !== 'OK').length;
  console.log(`Passed: ${ok}/${results.length}`);
  console.log(`Failed: ${failed}/${results.length}`);

  if (failed > 0) {
    console.log('');
    console.log('Failed pages:');
    results.filter(r => r.status !== 'OK').forEach(r => {
      console.log(`  - ${r.page}: ${r.status}`);
    });
  }
}

testPages().catch(console.error);
