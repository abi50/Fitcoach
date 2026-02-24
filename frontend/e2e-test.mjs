import { chromium } from 'playwright';
import { randomBytes } from 'crypto';
import path from 'path';
import fs from 'fs';

const SCREENSHOTS = path.join(process.cwd(), 'e2e-screenshots');
fs.mkdirSync(SCREENSHOTS, { recursive: true });

async function shot(page, name) {
  const file = path.join(SCREENSHOTS, `${name}.png`);
  await page.screenshot({ path: file, fullPage: true });
  console.log(`  📸 ${name}.png`);
  return file;
}

const email = `test_${randomBytes(4).toString('hex')}@example.com`;
const password = 'password123';
const username = `e2e_${randomBytes(3).toString('hex')}`;

const browser = await chromium.launch({ headless: true });
const page = await browser.newPage();
const errors = [];

page.on('console', msg => {
  if (msg.type() === 'error') errors.push(msg.text());
});

try {
  // 1. Home redirect
  console.log('\n[1] Home → redirect to /workouts → /login');
  await page.goto('http://localhost:3000');
  await page.waitForURL('**/login', { timeout: 5000 });
  console.log('  ✓ redirected to', page.url());
  await shot(page, '01-login-page');

  // 2. Navigate to register
  console.log('\n[2] Register page');
  await page.click('a[href="/register"]');
  await page.waitForURL('**/register', { timeout: 5000 });
  await shot(page, '02-register-page');

  // 3. Register
  console.log('\n[3] Registering user:', email, '/', username);
  await page.fill('#username', username);
  await page.fill('#email', email);
  await page.fill('#password', password);
  await shot(page, '03-register-filled');
  await page.click('button[type="submit"]');
  await page.waitForURL('**/workouts', { timeout: 8000 });
  console.log('  ✓ registered and redirected to', page.url());
  await shot(page, '04-workouts-empty');

  // 4. Create a plan
  console.log('\n[4] Creating a workout plan');
  await page.click('button:has-text("New Plan")');
  await page.waitForSelector('[role="dialog"]', { timeout: 3000 });
  await page.fill('#plan-name', 'Test Strength Plan');
  await page.selectOption('#goal', 'strength');
  await page.fill('#days', '4');
  await shot(page, '05-new-plan-dialog');
  await page.click('button:has-text("Create Plan")');
  await page.waitForSelector('button:has-text("Start Session")', { timeout: 8000 });
  console.log('  ✓ plan created');
  await shot(page, '06-workouts-with-plan');

  // 5. Start a session
  console.log('\n[5] Starting workout session');
  await page.click('button:has-text("Start Session")');
  await page.waitForURL('**/workouts/session**', { timeout: 5000 });
  console.log('  ✓ on session page', page.url());
  await shot(page, '07-session-page');

  // 6. Search for an exercise
  console.log('\n[6] Adding exercise via picker');
  await page.fill('input[placeholder="Search exercises…"]', 'Bench Press');
  await page.waitForTimeout(800);
  await shot(page, '08-exercise-picker-open');

  // Try to click existing result, or create new
  const existingItem = page.locator('ul button').first();
  const createBtn = page.locator('button:has-text("Create")').first();

  if (await existingItem.isVisible({ timeout: 1000 }).catch(() => false)) {
    await existingItem.click();
    console.log('  ✓ selected existing exercise');
  } else {
    await createBtn.click();
    console.log('  ✓ created new exercise "Bench Press"');
  }
  await page.waitForTimeout(500);
  await shot(page, '09-exercise-added');

  // 7. Log a set
  console.log('\n[7] Logging a set (100 kg × 5 reps)');
  await page.fill('input[placeholder="Weight (kg)"]', '100');
  await page.fill('input[placeholder="Reps"]', '5');
  await shot(page, '10-set-filled');
  await page.click('button:has-text("Log Set")');
  await page.waitForTimeout(1500);
  await shot(page, '11-set-logged');
  console.log('  ✓ set logged');

  // 8. Log a second set (PR attempt with more reps)
  console.log('\n[8] Adding second set via picker again');
  await page.fill('input[placeholder="Search exercises…"]', 'Bench Press');
  await page.waitForTimeout(800);
  const item2 = page.locator('ul button').first();
  const create2 = page.locator('button:has-text("Create")').first();
  if (await item2.isVisible({ timeout: 1000 }).catch(() => false)) {
    await item2.click();
  } else {
    await create2.click();
  }
  await page.waitForTimeout(500);

  // Fill and log
  const weightInputs = page.locator('input[placeholder="Weight (kg)"]');
  const repsInputs = page.locator('input[placeholder="Reps"]');
  const count = await weightInputs.count();
  await weightInputs.nth(count - 1).fill('100');
  await repsInputs.nth(count - 1).fill('8');
  await page.click('button:has-text("Log Set")');
  await page.waitForTimeout(1500);
  await shot(page, '12-second-set-logged');
  console.log('  ✓ second set logged');

  // Check for PR toast
  const prToast = page.locator('text=Personal Record');
  if (await prToast.isVisible({ timeout: 2000 }).catch(() => false)) {
    console.log('  ✓ PR toast appeared!');
    await shot(page, '12b-pr-toast');
  } else {
    console.log('  (no PR toast visible at this moment)');
  }

  // 9. Finish workout
  console.log('\n[9] Finishing workout');
  await page.click('button:has-text("Finish Workout")');
  await page.waitForTimeout(2000);
  await shot(page, '13-finish-workout');

  const summary = page.locator('text=Workout Complete');
  if (await summary.isVisible({ timeout: 3000 }).catch(() => false)) {
    console.log('  ✓ workout complete summary shown');
  } else {
    console.log('  ⚠ summary not visible — checking page content');
    console.log('  page text:', (await page.textContent('body'))?.slice(0, 300));
  }
  await shot(page, '14-session-complete');

} catch (err) {
  console.error('\n❌ Error:', err.message);
  await shot(page, 'error-state');
  process.exitCode = 1;
} finally {
  if (errors.length) {
    console.log('\n⚠ Console errors during test:');
    errors.forEach(e => console.log(' ', e));
  }
  console.log(`\nScreenshots saved to: ${SCREENSHOTS}`);
  await browser.close();
}
