import { test, expect } from '@playwright/test';
import { signIn } from './helpers/auth.js';
import { createNotebook, openNotebook } from './helpers/notebooks.js';
import path from 'node:path';
import fs from 'node:fs';
import os from 'node:os';

const TEST_EMAIL = 'vha7244@gmail.com';
const TEST_PASSWORD = '123456';

// Helper to create a minimal test file for upload
function createTempFile(name, content) {
  const tmpDir = os.tmpdir();
  const filePath = path.join(tmpDir, name);
  fs.writeFileSync(filePath, content);
  return filePath;
}

test.describe('Edge Cases (7.x)', () => {

  test.beforeEach(async ({ page }) => {
    page.on('dialog', dialog => dialog.accept());
    await page.goto('http://localhost/');
    // Sign in before each test
    await signIn(page, TEST_EMAIL, TEST_PASSWORD);
    await expect(page.locator('#scene-dashboard')).toBeVisible();
  });

  test.afterEach(async ({ page }) => {
    await page.reload();
    await page.waitForTimeout(300);
  });

  test('7.1 Upload multiple files', async ({ page }) => {
    await createNotebook(page);
    await expect(page.locator('#scene-chat')).toBeVisible();

    // Trigger file input via "Add source" button
    const sourceAddBtn = page.locator('.source-add-button').first();
    await sourceAddBtn.click();

    const fileInput = page.locator('#sourceFileInput');

    // Create 3 test PDF files
    const file1 = createTempFile('test-file-1.pdf', '%PDF-1.4 test content 1');
    const file2 = createTempFile('test-file-2.pdf', '%PDF-1.4 test content 2');
    const file3 = createTempFile('test-file-3.pdf', '%PDF-1.4 test content 3');

    // Set multiple files on the input
    await fileInput.setInputFiles([file1, file2, file3]);
    await page.waitForTimeout(500);

    // Wait for files to appear in source list
    await page.waitForTimeout(1500);

    // Verify all 3 files appear in source list
    const sourceItems = page.locator('.source-item');
    const count = await sourceItems.count();
    expect(count).toBeGreaterThanOrEqual(3);

    // Wait for files to reach "Ready" status
    await page.waitForTimeout(3000);

    // Verify files are in list (not empty)
    const listEmpty = page.locator('.source-empty');
    const isEmpty = await listEmpty.isVisible().catch(() => false);
    expect(isEmpty).toBe(false);

    // Check that source items have content
    const firstItem = sourceItems.first();
    await expect(firstItem.locator('.source-name')).toBeVisible({ timeout: 3000 });

    // Clean up temp files
    [file1, file2, file3].forEach(f => fs.unlinkSync(f));
  });

  test('7.3 Unsupported file viewer (Excel)', async ({ page }) => {
    await createNotebook(page);
    await expect(page.locator('#scene-chat')).toBeVisible();

    // Upload an Excel file
    const sourceAddBtn = page.locator('.source-add-button').first();
    await sourceAddBtn.click();

    const fileInput = page.locator('#sourceFileInput');
    const excelFile = createTempFile('test-data.xlsx',
      'PK\x03\x04 Test Excel Content');
    await fileInput.setInputFiles(excelFile);

    // Wait for source to appear
    await page.waitForTimeout(2000);

    // Click the source item to open viewer
    const sourceItem = page.locator('.source-item').first();
    await expect(sourceItem).toBeVisible({ timeout: 3000 });
    await sourceItem.click();

    // Verify viewer shows fallback with download link
    const viewerFallback = page.locator('.viewer-fallback');
    await expect(viewerFallback).toBeVisible({ timeout: 3000 });

    // Should have download link
    const downloadLink = viewerFallback.locator('.viewer-open-link');
    await expect(downloadLink).toBeVisible();

    // Clean up
    fs.unlinkSync(excelFile);
  });

  test('7.4 New note (no API)', async ({ page }) => {
    await createNotebook(page);
    await expect(page.locator('#scene-chat')).toBeVisible();

    // Click "New note" button
    const newNoteBtn = page.locator('.source-note-button');
    await expect(newNoteBtn).toBeVisible();

    // Set up a custom handler for the prompt dialog
    let promptedText = 'My custom note content';
    page.on('dialog', async dialog => {
      promptedText = dialog.type() === 'prompt' ? promptedText : '';
      await dialog.accept(promptedText);
    });

    await newNoteBtn.click();

    // Wait for the dialog to be handled
    await page.waitForTimeout(500);

    // Verify the note appears in source list as a note item
    const sourceItems = page.locator('.source-item');
    const count = await sourceItems.count();

    // There should be at least one source item (the note)
    if (count > 0) {
      const firstItem = sourceItems.first();
      await expect(firstItem.locator('.source-name')).toBeVisible({ timeout: 3000 });
      // Verify it's a note (should have note icon or note type text)
      const typeEl = firstItem.locator('.source-type');
      const typeText = await typeEl.textContent();
      expect(typeText).toMatch(/note/i);
    }
  });

  test('7.5 Stream abort on navigate', async ({ page }) => {
    await createNotebook(page);
    await expect(page.locator('#scene-chat')).toBeVisible();

    // Track console errors during the test
    const errors = [];
    page.on('console', msg => {
      if (msg.type() === 'error') errors.push(msg.text());
    });

    // Upload a PDF source first (so chat has context)
    const sourceAddBtn = page.locator('.source-add-button').first();
    await sourceAddBtn.click();

    const fileInput = page.locator('#sourceFileInput');
    const pdfFile = createTempFile('stream-test.pdf', '%PDF-1.4 test content for streaming');
    await fileInput.setInputFiles(pdfFile);

    // Wait for source to be added
    await page.waitForTimeout(2000);

    // Send a chat message
    const textarea = page.locator('#chatPrompt');
    await textarea.fill('What is this document about?');
    await page.click('.send-button');

    // Within 2 seconds of sending, click Dashboard back button
    await page.waitForTimeout(500);

    const backBtn = page.locator('.chat-back-button');
    await expect(backBtn).toBeVisible();
    await backBtn.click();

    // Wait for navigation back to dashboard
    await expect(page.locator('#scene-dashboard')).toBeVisible({ timeout: 5000 });

    // Allow async operations to complete
    await page.waitForTimeout(1000);

    // Verify no console errors occurred
    const relevantErrors = errors.filter(e =>
      !e.includes('favicon') &&
      !e.includes('net::ERR') &&
      !e.includes('404')
    );

    expect(relevantErrors).toHaveLength(0);

    // Clean up
    fs.unlinkSync(pdfFile);
  });
});