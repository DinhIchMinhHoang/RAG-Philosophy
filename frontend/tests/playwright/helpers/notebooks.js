/**
 * Notebook helper functions for Playwright E2E tests.
 * These helpers encapsulate common notebook management flows.
 */

/**
 * Create a new notebook and return its title.
 * Flow: Click "Create new notebook" → wait for ChatScene → return notebook title.
 * @param {import('@playwright/test').Page} page
 * @returns {Promise<string>} The title of the newly created notebook.
 */
export async function createNotebook(page) {
    // Click "Create new notebook" button
    await page.click('.create-button');

    // Wait for ChatScene to appear
    await page.waitForSelector('#scene-chat', { state: 'visible' });

    // Get the notebook title from the chat header
    const title = await page.locator('.chat-title').textContent();

    return title;
}

/**
 * Open a notebook by title from the dashboard.
 * Flow: From dashboard, click notebook with matching title → wait for ChatScene.
 * Uses first() to handle duplicate titles from previous test runs.
 * @param {import('@playwright/test').Page} page
 * @param {string} title - The title of the notebook to open.
 */
export async function openNotebook(page, title) {
    // Find the first notebook item with matching title and click it
    const notebookItem = page.locator(`.notebook-item[data-title="${title}"]`).first();
    await notebookItem.click();

    // Wait for ChatScene to appear
    await page.waitForSelector('#scene-chat', { state: 'visible' });
}

/**
 * Open the more (⋮) menu for a notebook by title.
 * Flow: Click the ⋮ button on the notebook card.
 * Uses first() to handle duplicate titles from previous test runs.
 * @param {import('@playwright/test').Page} page
 * @param {string} title - The title of the notebook.
 */
export async function openMoreMenu(page, title) {
    // Find the first notebook item and click its more button
    const notebookItem = page.locator(`.notebook-item[data-title="${title}"]`).first();
    await notebookItem.locator('.more-btn').click();
}

/**
 * Delete a notebook by title.
 * Flow: Open more menu → click Delete → confirm the browser dialog.
 * @param {import('@playwright/test').Page} page
 * @param {string} title - The title of the notebook to delete.
 */
export async function deleteNotebook(page, title) {
    // Open the more menu
    await openMoreMenu(page, title);

    // Handle the browser confirm dialog (accept it)
    page.on('dialog', dialog => dialog.accept());

    // Click the "Delete" menu item in the more menu
    await page.click('.more-menu .menu-item.delete');
}