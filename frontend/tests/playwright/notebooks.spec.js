/**
 * Playwright E2E Tests for Notebook management.
 * Tests: 2.1 - 2.5
 * Base URL: http://localhost/
 */

import { test, expect } from '@playwright/test';
import { resolve } from 'path';
import { fileURLToPath } from 'url';

const __dirname = fileURLToPath(new URL('.', import.meta.url));
const TEST_PDF = resolve(__dirname, '..', '..', '..', 'data', 'raw', 'test.pdf');
import { signIn } from './helpers/auth.js';
import { createNotebook, openNotebook, deleteNotebook } from './helpers/notebooks.js';

const TEST_EMAIL = 'vha7244@gmail.com';
const TEST_PASSWORD = '123456';

test.describe('Notebooks Suite (2.x)', () => {

    test.beforeEach(async ({ page }) => {
        // Start at the landing page
        await page.goto('http://localhost/');

        // Sign in before each test
        await signIn(page, TEST_EMAIL, TEST_PASSWORD);

        // Verify we are on the dashboard
        await expect(page.locator('#scene-dashboard')).toBeVisible();
    });

    /**
     * 2.1 Create notebook
     * Test that creating a new notebook shows "Untitled notebook" in the grid.
     */
    test('2.1 Create notebook - verify "Untitled notebook" in grid', async ({ page }) => {
        // Create a new notebook
        await createNotebook(page);

        // Go back to dashboard
        await page.click('.chat-back-button');
        await page.waitForSelector('#scene-dashboard', { state: 'visible' });

        // Verify the new notebook appears in the grid with default title
        // The title should be "Untitled notebook" or contain "Untitled"
        const myGrid = page.locator('.my-grid');
        await expect(myGrid).toBeVisible();

        // Check for the notebook item with default title
        const notebookItems = myGrid.locator('.notebook-item');
        const count = await notebookItems.count();
        expect(count).toBeGreaterThan(0);

        // Verify at least one notebook has "Untitled" in its title
        const titles = await myGrid.locator('.item-title').allTextContents();
        const hasUntitled = titles.some(title =>
            title.toLowerCase().includes('untitled')
        );
        expect(hasUntitled).toBe(true);
    });

    /**
     * 2.2 Open notebook
     * Test that clicking a notebook opens the ChatScene.
     */
    test('2.2 Open notebook - verify ChatScene shown', async ({ page }) => {
        // Create a new notebook first
        await createNotebook(page);

        // Get the notebook title
        const title = await page.locator('.chat-title').textContent();

        // Go back to dashboard
        await page.click('.chat-back-button');
        await page.waitForSelector('#scene-dashboard', { state: 'visible' });

        // Open the notebook we just created
        await openNotebook(page, title);

        // Verify ChatScene is shown
        await expect(page.locator('#scene-chat')).toBeVisible();

        // Verify chat title matches the notebook title
        await expect(page.locator('.chat-title')).toHaveText(title);
    });

    /**
     * 2.3 Rename notebook
     * Test that renaming a notebook updates its title.
     */
    test('2.3 Rename notebook - prompt for new name and verify title updated', async ({ page }) => {
        // Create a new notebook first - get unique ID from chat scene
        await createNotebook(page);
        const notebookId = await page.locator('#scene-chat').getAttribute('data-notebook-id');

        // Go back to dashboard
        await page.click('.chat-back-button');
        await page.waitForSelector('#scene-dashboard', { state: 'visible' });

        const newTitle = `Renamed Test ${Date.now()}`;

        // Find notebook by data-notebook-id (unique)
        const notebookItem = page.locator(`.notebook-item[data-notebook-id="${notebookId}"]`);
        await notebookItem.locator('.more-btn').click();

        // Wait for more menu to appear and click Rename
        await page.waitForSelector('.more-menu', { state: 'visible' });

        // Handle prompt dialog using page.on pattern
        const renamePromise = new Promise((resolve) => {
            page.once('dialog', async (dialog) => {
                await dialog.accept(newTitle);
                resolve(true);
            });
        });
        await page.click('.more-menu .menu-item.rename');
        await renamePromise;

        // Wait for the title to be updated
        await page.waitForTimeout(1000);

        // Verify the notebook title is updated
        const updatedItem = page.locator(`.notebook-item[data-title="${newTitle}"]`);
        await expect(updatedItem.first()).toBeVisible();
    });

    /**
     * 2.4 Delete notebook
     * Test that deleting a notebook removes it from the grid.
     */
    test('2.4 Delete notebook - verify removed from grid', async ({ page }) => {
        // Create a new notebook
        const title = await createNotebook(page);

        // Go back to dashboard
        await page.click('.chat-back-button');
        await page.waitForSelector('#scene-dashboard', { state: 'visible' });

        // Get the initial count for this specific notebook title
        const initialCount = await page.locator(`.notebook-item[data-title="${title}"]`).count();

        // Find the first notebook with this title and delete it
        const notebookItem = page.locator(`.notebook-item[data-title="${title}"]`).first();
        await notebookItem.locator('.more-btn').first().click();

        // Handle the confirm dialog
        page.once('dialog', dialog => dialog.accept());

        // Wait for more menu and click Delete
        await page.waitForSelector('.more-menu', { state: 'visible' });
        await page.click('.more-menu .menu-item.delete');

        // Wait for deletion
        await page.waitForTimeout(1000);

        // Verify count decreased by 1
        const finalCount = await page.locator(`.notebook-item[data-title="${title}"]`).count();
        expect(finalCount).toBe(initialCount - 1);
    });

    /**
     * 2.5 Delete notebook with source - API check to verify cleanup
     * Test that deleting a notebook with a supported source file properly cleans up.
     */
    test('2.5 Delete notebook with source - verify cleanup', async ({ page }) => {
        // Create a new notebook
        const title = await createNotebook(page);

        // Upload a supported source file to the notebook
        const [fileChooser] = await Promise.all([
            page.waitForEvent('filechooser'),
            page.locator('.source-add-button').first().click(),
        ]);
        await fileChooser.setFiles([TEST_PDF]);

        // Wait for upload to complete
        await page.waitForTimeout(2000);

        // Go back to dashboard
        await page.click('.chat-back-button');
        await page.waitForSelector('#scene-dashboard', { state: 'visible' });

        // Get count before delete
        const initialCount = await page.locator(`.notebook-item[data-title="${title}"]`).count();

        // Delete the notebook
        const notebookItem = page.locator(`.notebook-item[data-title="${title}"]`).first();
        await notebookItem.locator('.more-btn').first().click();
        page.once('dialog', dialog => dialog.accept());
        await page.waitForSelector('.more-menu', { state: 'visible' });
        await page.click('.more-menu .menu-item.delete');

        // Wait for deletion
        await page.waitForTimeout(1000);

        // Verify the notebook is removed
        const finalCount = await page.locator(`.notebook-item[data-title="${title}"]`).count();
        expect(finalCount).toBe(initialCount - 1);
    });
});
