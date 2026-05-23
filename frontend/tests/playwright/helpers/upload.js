/**
 * Upload helper functions for Playwright E2E tests.
 * These helpers encapsulate file upload flows and upload state checks.
 */

/**
 * Upload a file to the current notebook.
 * Flow: Click "Add source" button → wait for file chooser → set files → return result.
 * @param {import('@playwright/test').Page} page
 * @param {string} filePath - Absolute path to the file to upload.
 * @returns {Promise<Object>} Upload result with status info.
 */
export async function uploadFile(page, filePath) {
    // Wait for the source add button and click it, waiting for file chooser
    const [fileChooser] = await Promise.all([
        page.waitForEvent('filechooser'),
        page.locator('.source-add-button').first().click()
    ]);

    // Set the files to upload
    await fileChooser.setFiles([filePath]);

    // Return a simple result indicating upload was initiated
    return { started: true };
}

/**
 * Wait for all uploads to complete.
 * Polls until no source item has status "Uploading" or "Queued".
 * @param {import('@playwright/test').Page} page
 * @param {number} timeoutMs - Maximum time to wait in milliseconds. Default 120000 (2 minutes).
 */
export async function waitForUploadComplete(page, timeoutMs = 120000) {
    const startTime = Date.now();

    while (true) {
        // Check if we've exceeded the timeout
        if (Date.now() - startTime > timeoutMs) {
            throw new Error(`Upload wait timed out after ${timeoutMs}ms`);
        }

        // Get all source items and their status
        const statusText = await page.evaluate(() => {
            const items = document.querySelectorAll('.source-item');
            return Array.from(items).map(item => item.querySelector('.source-type')?.textContent || '');
        });

        // Check if any item is still uploading or queued
        const stillUploading = statusText.some(status =>
            status.includes('Uploading') || status.includes('Queued')
        );

        if (!stillUploading) {
            // All uploads complete
            return;
        }

        // Wait a bit before checking again
        await page.waitForTimeout(1000);
    }
}

/**
 * Get all source items in the source list.
 * @param {import('@playwright/test').Page} page
 * @returns {Promise<Array>} Array of source item elements.
 */
export async function getSourceItems(page) {
    return await page.locator('.source-item').all();
}