import { test, expect } from '@playwright/test';
import { signIn } from './helpers/auth.js';
import { createNotebook, openNotebook } from './helpers/notebooks.js';

const TEST_EMAIL = 'vha7244@gmail.com';
const TEST_PASSWORD = '123456';

test.describe('Dashboard UI (5.x)', () => {

  test.beforeEach(async ({ page }) => {
    page.on('dialog', dialog => dialog.accept());
    await page.goto('http://localhost/');
    await signIn(page, TEST_EMAIL, TEST_PASSWORD);
    await expect(page.locator('#scene-dashboard')).toBeVisible();
  });

  test.afterEach(async ({ page }) => {
    await page.reload();
    await page.waitForTimeout(300);
  });

  test('5.1 Grid ↔ List toggle', async ({ page }) => {
    // Should start in grid view (active button)
    const gridBtn = page.locator('.view-option[data-view="grid"]');
    await expect(gridBtn).toHaveClass(/active/);

    // Get initial state of the dashboard container
    const dashboard = page.locator('#scene-dashboard .dashboard-container');
    const initialView = await dashboard.getAttribute('data-view');
    expect(initialView).toBeFalsy(); // defaults to grid

    // Click List button (format_list_bulleted icon)
    const listBtn = page.locator('.view-option[data-view="list"]');
    await listBtn.click();

    // Wait for CSS transition (150ms + buffer)
    await page.waitForTimeout(400);

    // Verify layout changed to list
    const listView = await dashboard.getAttribute('data-view');
    expect(listView).toBe('list');

    // List button should now be active
    await expect(listBtn).toHaveClass(/active/);
    await expect(gridBtn).not.toHaveClass(/active/);

    // Click Grid button to switch back
    await gridBtn.click();
    await page.waitForTimeout(400);

    // Verify layout changed back to grid
    const gridView = await dashboard.getAttribute('data-view');
    expect(gridView).toBe('grid');
    await expect(gridBtn).toHaveClass(/active/);
  });

  test('5.2 Cover image upload', async ({ page }) => {
    // Create a notebook (goes directly to chat)
    await createNotebook(page);
    await expect(page.locator('#scene-chat')).toBeVisible();

    // Go back to dashboard to see the notebook card
    await page.click('.chat-back-button');
    await page.waitForSelector('#scene-dashboard', { state: 'visible' });

    // Open more menu (⋮) on the first notebook item
    const moreBtn = page.locator('.notebook-item .more-btn').first();
    await moreBtn.click();
    await page.waitForTimeout(200);

    // Click "Change image"
    const changeImageItem = page.locator('.more-menu .menu-item', { hasText: 'Change image' });
    await expect(changeImageItem).toBeVisible();
    await changeImageItem.click();

    // Modal should open
    const modal = page.locator('#imageModal');
    await expect(modal).toBeVisible({ timeout: 3000 });

    // Click "Upload" tab (should be active by default)
    const uploadTab = page.locator('#imageModal .tab[data-tab="upload"]');
    await expect(uploadTab).toHaveClass(/active/);

    // Click "Choose file" button to trigger file input
    const fileInput = page.locator('#imageFileInput');
    await expect(page.locator('#chooseFileBtn')).toBeVisible();

    // Create a minimal 1x1 PNG in temp dir
    const fs = await import('node:fs');
    const path = await import('node:path');
    const os = await import('node:os');

    const tmpDir = os.tmpdir();
    const testImagePath = path.join(tmpDir, 'test-cover-image.png');
    const pngData = Buffer.from([
      0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a,
      0x00, 0x00, 0x00, 0x0d, 0x49, 0x48, 0x44, 0x52,
      0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x01,
      0x08, 0x02, 0x00, 0x00, 0x00, 0x90, 0x77, 0x53,
      0xde, 0x00, 0x00, 0x00, 0x0c, 0x49, 0x44, 0x41,
      0x54, 0x08, 0xd7, 0x63, 0xf8, 0xcf, 0xc0, 0x00,
      0x00, 0x00, 0x03, 0x00, 0x01, 0x00, 0x18, 0xdd,
      0x8d, 0xb4, 0x00, 0x00, 0x00, 0x00, 0x49, 0x45,
      0x4e, 0x44, 0xae, 0x42, 0x60, 0x82,
    ]);
    fs.writeFileSync(testImagePath, pngData);

    // Set the file on the file input
    await fileInput.setInputFiles(testImagePath);
    await page.waitForTimeout(300);

    // Image preview should update
    const preview = page.locator('#imagePreview');
    await expect(preview).toBeVisible({ timeout: 3000 });

    // Click Apply
    await page.locator('#applyCoverBtn').click();
    await page.waitForTimeout(500);

    // Modal should close
    await expect(modal).not.toBeVisible();

    // Verify cover element style changed
    const coverEl = page.locator('.notebook-item').first().locator('.cover');
    const style = await coverEl.getAttribute('style');
    expect(style).toBeTruthy();
    expect(style).toMatch(/background/);

    // Clean up
    fs.unlinkSync(testImagePath);
  });

  test('5.3 Cover color', async ({ page }) => {
    // Create a notebook
    await createNotebook(page);
    await expect(page.locator('#scene-chat')).toBeVisible();

    // Go back to dashboard
    await page.click('.chat-back-button');
    await page.waitForSelector('#scene-dashboard', { state: 'visible' });

    // Open more menu
    const moreBtn = page.locator('.notebook-item .more-btn').first();
    await moreBtn.click();
    await page.waitForTimeout(200);

    // Click "Change image"
    const changeImageItem = page.locator('.more-menu .menu-item', { hasText: 'Change image' });
    await changeImageItem.click();

    // Modal should open
    const modal = page.locator('#imageModal');
    await expect(modal).toBeVisible({ timeout: 3000 });

    // Click "Color" tab
    const colorTab = page.locator('#imageModal .tab[data-tab="color"]');
    await colorTab.click();
    await expect(colorTab).toHaveClass(/active/);

    // Pick a color via #colorPicker
    const colorPicker = page.locator('#colorPicker');
    await expect(colorPicker).toBeVisible();
    await colorPicker.fill('#FF5733');
    await page.waitForTimeout(200);

    // Color preview should update
    await expect(page.locator('#colorPreview')).toBeVisible();

    // Click Apply
    await page.locator('#applyCoverBtn').click();
    await page.waitForTimeout(500);

    // Modal should close
    await expect(modal).not.toBeVisible();

    // Verify cover color updated
    const coverEl = page.locator('.notebook-item').first().locator('.cover');
    const style = await coverEl.getAttribute('style');
    expect(style).toBeTruthy();
  });

  test('5.4 Show All', async ({ page }) => {
    // Create a couple of notebooks
    await createNotebook(page);
    await page.click('.chat-back-button');
    await page.waitForSelector('#scene-dashboard', { state: 'visible' });
    await createNotebook(page);
    await page.waitForTimeout(300);

    // Click "Show all" button
    const showAllBtn = page.locator('.my-section .show-all-btn');
    await expect(showAllBtn).toBeVisible();
    await showAllBtn.click();

    // Verify transition to show-all scene
    const showallScene = page.locator('#scene-showall');
    await expect(showallScene).toBeVisible({ timeout: 3000 });

    // Verify notebooks are displayed in the showall grid
    const showallGrid = page.locator('.showall-grid');
    await expect(showallGrid).toBeVisible();
    await expect(page.locator('.showall-grid .notebook-item').first()).toBeVisible({ timeout: 3000 });

    // Verify close button works to return to dashboard
    const closeBtn = page.locator('.close-showall-btn');
    await expect(closeBtn).toBeVisible();
    await closeBtn.click();

    // Should be back on dashboard
    await expect(page.locator('#scene-dashboard')).toBeVisible();
    await expect(showallScene).not.toBeVisible();
  });
});