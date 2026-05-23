/**
 * Auth helper utilities for Playwright E2E tests.
 * Provides common sign-up/sign-in helpers that create fresh test users.
 */

/**
 * Generate a unique test email address.
 * @param {string} prefix - Prefix for the email (default: 'test')
 * @returns {string} Unique email address
 */
export function uniqueEmail(prefix = 'test') {
  const ts = Date.now();
  const rand = Math.floor(Math.random() * 99999);
  return `${prefix}${ts}${rand}@lumina.test`;
}

/**
 * Generate a unique test username.
 * @param {string} prefix - Prefix for the username (default: 'user')
 * @returns {string} Unique username
 */
export function uniqueUsername(prefix = 'user') {
  const ts = Date.now();
  const rand = Math.floor(Math.random() * 99999);
  return `${prefix}${ts}${rand}`;
}

/**
 * Sign in an existing user with email and password.
 * @param {import('@playwright/test').Page} page
 * @param {string} email - User email
 * @param {string} password - User password
 */
export async function signIn(page, email, password) {
  await page.goto('http://localhost/');
  await page.waitForSelector('[data-scene="signin"]');
  await page.click('[data-scene="signin"]');
  await page.waitForSelector('#signin-form', { state: 'visible' });

  await page.fill('#signin-email', email);
  await page.fill('#signin-password', password);

  await page.click('#signin-form button[type="submit"]');
  await page.waitForURL('**/', { timeout: 15000 });
  await page.waitForSelector('#scene-dashboard', { state: 'visible', timeout: 10000 });
}

/**
 * Sign up a new user with specified credentials.
 * @param {import('@playwright/test').Page} page
 * @param {string} username - Username
 * @param {string} email - Email
 * @param {string} password - Password
 */
export async function signUp(page, username, email, password) {
  await page.goto('http://localhost/');
  await page.waitForSelector('[data-scene="signup"]');
  await page.click('[data-scene="signup"]');
  await page.waitForSelector('#signup-form', { state: 'visible' });

  await page.fill('#signup-username', username);
  await page.fill('#signup-email', email);
  await page.fill('#signup-password', password);
  await page.fill('#signup-confirm-password', password);

  await page.click('#signup-form button[type="submit"]');
  await page.waitForURL('**/', { timeout: 15000 });
  await page.waitForSelector('#scene-dashboard', { state: 'visible', timeout: 10000 });
}

/**
 * Sign out the current user.
 * @param {import('@playwright/test').Page} page
 */
export async function signOut(page) {
  // Go to account scene and click logout
  await page.click('.account-button');
  await page.waitForSelector('#scene-account', { state: 'visible' });
  await page.click('.logout-button');
  await page.waitForSelector('#scene-landing', { state: 'visible', timeout: 5000 });
}

/**
 * Sign up a new user with random credentials.
 * @param {import('@playwright/test').Page} page
 * @param {object} options
 * @param {string} [options.email] - Email to use (auto-generated if not provided)
 * @param {string} [options.username] - Username to use (auto-generated if not provided)
 * @param {string} [options.password] - Password to use (default: 'TestPass123!')
 * @returns {Promise<{email: string, username: string, password: string}>}
 */
export async function signUpNewUser(page, { email, username, password = 'TestPass123!' } = {}) {
  const finalEmail = email || uniqueEmail();
  const finalUsername = username || uniqueUsername();

  await signUp(page, finalUsername, finalEmail, password);

  return { email: finalEmail, username: finalUsername, password };
}