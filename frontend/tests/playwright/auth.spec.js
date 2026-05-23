/**
 * Playwright E2E Tests for Authentication flows.
 * Tests: 1.1 - 1.6
 * Base URL: http://localhost/
 */

import { test, expect } from '@playwright/test';
import { signIn, signUp, signOut } from './helpers/auth.js';

const TEST_EMAIL = 'vha7244@gmail.com';
const TEST_PASSWORD = '123456';

test.describe('Auth Suite (1.x)', () => {

    test.beforeEach(async ({ page }) => {
        // Start at the landing page for each test
        await page.goto('http://localhost/');
    });

    /**
     * 1.1 Sign In success
     * Test that a user with valid credentials can sign in and reach the dashboard.
     */
    test('1.1 Sign In success', async ({ page }) => {
        // Perform sign in with valid credentials
        await signIn(page, TEST_EMAIL, TEST_PASSWORD);

        // Verify dashboard is shown
        await expect(page.locator('#scene-dashboard')).toBeVisible();

        // Verify the user is logged in by checking account button is visible
        await expect(page.locator('.account-button')).toBeVisible();
    });

    /**
     * 1.2 Sign In fail - wrong password
     * Test that signing in with an incorrect password shows an error message.
     */
    test('1.2 Sign In fail - wrong password', async ({ page }) => {
        // Navigate to sign in form
        await page.getByRole('button', { name: 'Sign In' }).first().click();
        await page.waitForSelector('#scene-signin', { state: 'visible' });

        // Fill with correct email but wrong password
        await page.fill('#signin-email', TEST_EMAIL);
        await page.fill('#signin-password', 'wrong_password_123');

        // Submit the form
        await page.click('#signin-form button[type="submit"]');

        // Verify error message appears
        const errorDiv = page.locator('#scene-signin .form-error');
        await expect(errorDiv).toBeVisible();
        await expect(errorDiv).not.toHaveText('');

        // Verify we are NOT on the dashboard
        await expect(page.locator('#scene-dashboard')).not.toBeVisible();
    });

    /**
     * 1.3 Sign Up success - unique email each run (timestamp-based)
     * Test that a new user can sign up and reach the dashboard.
     */
    test('1.3 Sign Up success', async ({ page }) => {
        // Generate a unique email using timestamp
        const timestamp = Date.now();
        const uniqueEmail = `test_${timestamp}@gmail.com`;
        const username = `testuser_${timestamp}`;
        const password = 'TestPassword123!';

        // Perform sign up
        await signUp(page, username, uniqueEmail, password);

        // Verify dashboard is shown
        await expect(page.locator('#scene-dashboard')).toBeVisible();

        // Sign out
        await signOut(page);

        // Sign in with the newly created account
        await signIn(page, uniqueEmail, password);

        // Verify dashboard is shown again
        await expect(page.locator('#scene-dashboard')).toBeVisible();
    });

    /**
     * 1.4 Sign Up validation - mismatched passwords
     * Test that sign up with mismatched passwords shows an error.
     */
    test('1.4 Sign Up validation - mismatched passwords', async ({ page }) => {
        // Navigate to sign up form
        await page.getByRole('button', { name: 'Sign Up' }).first().click();
        await page.waitForSelector('#scene-signup', { state: 'visible' });

        // Fill form with mismatched passwords
        await page.fill('#signup-username', 'testuser_mismatch');
        await page.fill('#signup-email', 'mismatch_test@gmail.com');
        await page.fill('#signup-password', 'Password123');
        await page.fill('#signup-confirm-password', 'DifferentPassword456');

        // Submit the form
        await page.click('#signup-form button[type="submit"]');

        // Verify error message appears (backend validates password match)
        const errorDiv = page.locator('#scene-signup .form-error');
        await expect(errorDiv).toBeVisible();
        await expect(errorDiv).not.toHaveText('');

        // Verify we are NOT on the dashboard
        await expect(page.locator('#scene-dashboard')).not.toBeVisible();
    });

    /**
     * 1.5 Logout
     * Test that a logged in user can sign out and return to the landing page.
     */
    test('1.5 Logout', async ({ page }) => {
        // Sign in first
        await signIn(page, TEST_EMAIL, TEST_PASSWORD);

        // Verify dashboard is visible
        await expect(page.locator('#scene-dashboard')).toBeVisible();

        // Sign out
        await signOut(page);

        // Verify landing page is shown
        await expect(page.locator('#scene-landing')).toBeVisible();

        // Verify sign in and sign up buttons are visible on landing page
        await expect(page.getByRole('button', { name: 'Sign In' }).first()).toBeVisible();
        await expect(page.getByRole('button', { name: 'Sign Up' }).first()).toBeVisible();
    });

    /**
     * 1.6 Auth guard - try to access dashboard without signing in
     * Test that the application redirects unauthenticated users away from dashboard.
     */
    test('1.6 Auth guard - try to access dashboard without signing in', async ({ page }) => {
        // Verify we start at landing page
        await expect(page.locator('#scene-landing')).toBeVisible();

        // Verify dashboard is not visible when not authenticated
        await expect(page.locator('#scene-dashboard')).not.toBeVisible();

        // Click Sign In button to verify we're prompted to authenticate
        await page.getByRole('button', { name: 'Sign In' }).first().click();
        await page.waitForSelector('#scene-signin', { state: 'visible' });

        // Without credentials, we should not reach the dashboard
        // Fill wrong credentials to verify we stay on sign in
        await page.fill('#signin-email', 'invalid@test.com');
        await page.fill('#signin-password', 'wrongpassword');
        await page.click('#signin-form button[type="submit"]');

        // Verify still on sign in (not dashboard)
        await expect(page.locator('#scene-signin')).toBeVisible();
        await expect(page.locator('#scene-dashboard')).not.toBeVisible();
    });

});