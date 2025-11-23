const puppeteer = require('puppeteer');
const path = require('path');
const fs = require('fs');

const BASE_URL = 'http://localhost:3005';
const OUTPUT_DIR = path.join(__dirname, '..', 'docs', 'screenshots');

const pages = [
  { name: 'login', path: '/login', requiresAuth: false },
  { name: 'dashboard', path: '/', requiresAuth: true },
  { name: 'entities', path: '/entities', requiresAuth: true },
  { name: 'organizations', path: '/organizations', requiresAuth: true },
  { name: 'software', path: '/software', requiresAuth: true },
  { name: 'services', path: '/services', requiresAuth: true },
  { name: 'issues', path: '/issues', requiresAuth: true },
  { name: 'projects', path: '/projects', requiresAuth: true },
  { name: 'identities', path: '/identities', requiresAuth: true },
  { name: 'keys', path: '/keys', requiresAuth: true },
  { name: 'secrets', path: '/secrets', requiresAuth: true },
  { name: 'dependencies', path: '/dependencies', requiresAuth: true },
  { name: 'discovery', path: '/discovery', requiresAuth: true },
  { name: 'profile', path: '/profile', requiresAuth: true },
];

async function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

async function captureScreenshots() {
  if (!fs.existsSync(OUTPUT_DIR)) {
    fs.mkdirSync(OUTPUT_DIR, { recursive: true });
  }

  const browser = await puppeteer.launch({
    headless: 'new',
    args: ['--no-sandbox', '--disable-setuid-sandbox'],
  });

  const page = await browser.newPage();
  await page.setViewport({ width: 1920, height: 1080 });

  console.log('Logging in...');
  await page.goto(`${BASE_URL}/login`, { waitUntil: 'networkidle0', timeout: 60000 });
  await page.waitForSelector('input[type="text"]', { timeout: 10000 });

  await page.type('input[type="text"]', 'admin');
  await page.type('input[type="password"]', 'admin123');
  await page.click('button[type="submit"]');

  await page.waitForFunction(
    () => !window.location.pathname.includes('/login'),
    { timeout: 30000 }
  );
  await sleep(2000);
  console.log('Logged in successfully');

  for (const pageInfo of pages) {
    try {
      console.log(`Capturing ${pageInfo.name}...`);

      if (!pageInfo.requiresAuth && pageInfo.path === '/login') {
        const incognitoContext = await browser.createBrowserContext();
        const incognitoPage = await incognitoContext.newPage();
        await incognitoPage.setViewport({ width: 1920, height: 1080 });
        await incognitoPage.goto(`${BASE_URL}${pageInfo.path}`, { waitUntil: 'networkidle0', timeout: 60000 });
        await sleep(1500);
        await incognitoPage.screenshot({
          path: path.join(OUTPUT_DIR, `${pageInfo.name}.png`),
          fullPage: false,
        });
        await incognitoContext.close();
      } else {
        await page.goto(`${BASE_URL}${pageInfo.path}`, { waitUntil: 'networkidle0', timeout: 60000 });
        await sleep(1500);
        await page.screenshot({
          path: path.join(OUTPUT_DIR, `${pageInfo.name}.png`),
          fullPage: false,
        });
      }

      console.log(`  Saved ${pageInfo.name}.png`);
    } catch (error) {
      console.error(`  Error capturing ${pageInfo.name}: ${error.message}`);
    }
  }

  await browser.close();
  console.log('\nScreenshots saved to:', OUTPUT_DIR);
}

captureScreenshots().catch(console.error);
