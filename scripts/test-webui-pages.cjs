const puppeteer = require('puppeteer');

// Configurable via environment variables for CI/CD flexibility
const BASE_URL = process.env.WEB_URL || 'http://localhost:3005';
const API_URL = process.env.API_URL || 'http://localhost:4000';

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
  { name: 'On-Call Rotations', path: '/on-call-rotations' },
  { name: 'Profile', path: '/profile' },
  { name: 'IPAM', path: '/ipam' },
  { name: 'Map', path: '/map' },
  { name: 'Audit Logs', path: '/audit' },
  { name: 'Relationship Graph', path: '/graph' },
  { name: 'Tenants', path: '/tenants' },
  { name: 'Register', path: '/register', skipAuth: true },
  { name: 'SSO Configuration', path: '/sso-config' },
  { name: 'SBOM Dashboard', path: '/sbom' },
  { name: 'Vulnerabilities', path: '/vulnerabilities' },
  { name: 'Service Endpoints', path: '/service-endpoints' },
  { name: 'Sync Config', path: '/sync-config' },
  { name: 'Search', path: '/search' },
  { name: 'Backups', path: '/backups' },
  { name: 'Networking', path: '/networking' },
  { name: 'Webhooks', path: '/webhooks' },
  { name: 'Admin Settings', path: '/admin' },
  { name: 'License Policies', path: '/license-policies' },
];

// Detail pages require existing IDs - test with ID 1 if it exists
const detailPages = [
  { name: 'Entity Detail', path: '/entities/1', testId: 1 },
  { name: 'Organization Detail', path: '/organizations/1', testId: 1 },
  { name: 'Tenant Detail', path: '/tenants/1', testId: 1 },
  { name: 'Project Detail', path: '/projects/1', testId: 1 },
  { name: 'Issue Detail', path: '/issues/1', testId: 1 },
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
    await inputs[0].type('admin@localhost.local');
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

  // Test function for pages
  async function testPage(pageInfo, results) {
    errors.length = 0;
    apiErrors.length = 0;

    console.log(`Testing: ${pageInfo.name} (${pageInfo.path})...`);

    try {
      await page.goto(`${BASE_URL}${pageInfo.path}`, { waitUntil: 'networkidle0', timeout: 60000 });
      await sleep(2000);

      const currentUrl = page.url();
      if (currentUrl.includes('/login') && !pageInfo.skipAuth) {
        console.log(`  REDIRECT: Redirected to login`);
        results.push({ page: pageInfo.name, status: 'REDIRECT', errors: [], apiErrors: [] });
        return;
      }

      // Check for tabs and test them
      const tabs = await page.$$('[role="tab"], .tab, .nav-tab');
      if (tabs.length > 0) {
        console.log(`  Found ${tabs.length} tabs, testing each...`);
        for (let i = 0; i < Math.min(tabs.length, 5); i++) {
          try {
            await tabs[i].click();
            await sleep(1000);
            console.log(`    Tab ${i + 1}: OK`);
          } catch (e) {
            console.log(`    Tab ${i + 1}: Error - ${e.message}`);
          }
        }
      }

      // Check for modals/dialogs by finding buttons with specific text
      try {
        const createButton = await page.evaluateHandle(() => {
          const buttons = Array.from(document.querySelectorAll('button'));
          return buttons.find(btn =>
            btn.textContent.includes('Create') ||
            btn.textContent.includes('Add') ||
            btn.textContent.includes('New')
          );
        });

        if (createButton && createButton.asElement()) {
          await createButton.asElement().click();
          await sleep(1000);
          const modal = await page.$('[role="dialog"], .modal, .dialog');
          if (modal) {
            console.log(`    Modal: OK`);
            // Close modal
            const closeButton = await page.evaluateHandle(() => {
              const buttons = Array.from(document.querySelectorAll('button'));
              return buttons.find(btn =>
                btn.textContent.includes('Cancel') ||
                btn.textContent.includes('Close')
              );
            });
            if (closeButton && closeButton.asElement()) {
              await closeButton.asElement().click();
            }
          }
        }
      } catch (e) {
        // Modal test is optional
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

  // Test each main page
  const results = [];
  for (const pageInfo of pages) {
    await testPage(pageInfo, results);
  }

  // Test detail pages (may 404 if no data exists)
  console.log('');
  console.log('Testing detail pages (may 404 if no test data)...');
  for (const pageInfo of detailPages) {
    await testPage(pageInfo, results);
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
