/**
 * Playwright configuration for E2E tests.
 * Tests are located in frontend/tests/playwright/
 */

import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
    testDir: './',
    testMatch: ['**/*.spec.js'],
    timeout: 60000, // 60 seconds default timeout
    expect: {
        timeout: 30000, // 30 seconds for expect assertions
    },
    fullyParallel: false, // Run tests serially to avoid conflicts
    forbidOnly: !!process.env.CI,
    retries: process.env.CI ? 2 : 0,
    workers: process.env.CI ? 1 : undefined,
    reporter: 'html',
    use: {
        baseURL: 'http://localhost',
        trace: 'on-first-retry',
        screenshot: 'only-on-failure',
        video: 'retain-on-failure',
        actionTimeout: 15000,
    },
    projects: [
        {
            name: 'chromium',
            use: { ...devices['Desktop Chrome'] },
        },
        // Uncomment to add more browser targets
        // {
        //     name: 'firefox',
        //     use: { ...devices['Desktop Firefox'] },
        // },
        // {
        //     name: 'webkit',
        //     use: { ...devices['Desktop Safari'] },
        // },
    ],
    webServer: {
        command: 'npx serve .',
        url: 'http://localhost',
        reuseExistingServer: !process.env.CI,
        timeout: 120000,
    },
});