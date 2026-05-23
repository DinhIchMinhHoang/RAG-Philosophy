import { test, expect } from '@playwright/test';
import { signIn } from './helpers/auth.js';
import { createNotebook, openNotebook } from './helpers/notebooks.js';

const TEST_EMAIL = 'vha7244@gmail.com';
const TEST_PASSWORD = '123456';

test.describe('Chat UX (6.x)', () => {

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

  test('6.1 Collapse Sources panel', async ({ page }) => {
    await createNotebook(page);
    await expect(page.locator('#scene-chat')).toBeVisible();

    // Verify sources panel is visible
    const sourcesPanel = page.locator('.chat-panel[data-panel="sources"]');
    await expect(sourcesPanel).toBeVisible();
    await expect(sourcesPanel).not.toHaveClass(/is-collapsed/);

    // Click the collapse button (chevron_left icon, data-collapse="sources")
    const collapseBtn = page.locator('.panel-toggle[data-collapse="sources"]');
    await expect(collapseBtn).toBeVisible();
    await collapseBtn.click();

    // Wait for CSS transition
    await page.waitForTimeout(300);

    // Verify panel collapsed
    await expect(sourcesPanel).toHaveClass(/is-collapsed/);

    // Panel rail (expand button) should be visible
    const expandRail = page.locator('.panel-rail-button[data-expand="sources"]');
    await expect(expandRail).toBeVisible();

    // Click expand button to restore
    await expandRail.click();
    await page.waitForTimeout(300);

    // Verify panel restored
    await expect(sourcesPanel).not.toHaveClass(/is-collapsed/);
    await expect(sourcesPanel.locator('.panel-header')).toBeVisible();
  });

  test('6.2 Collapse Source Viewer panel', async ({ page }) => {
    await createNotebook(page);
    await expect(page.locator('#scene-chat')).toBeVisible();

    // Verify tools panel is visible (Source Viewer)
    const toolsPanel = page.locator('.chat-panel[data-panel="tools"]');
    await expect(toolsPanel).toBeVisible();
    await expect(toolsPanel).not.toHaveClass(/is-collapsed/);

    // Click the right collapse button (data-collapse="tools")
    const collapseBtn = page.locator('.panel-toggle[data-collapse="tools"]');
    await expect(collapseBtn).toBeVisible();
    await collapseBtn.click();

    // Wait for CSS transition
    await page.waitForTimeout(300);

    // Verify viewer panel collapsed
    await expect(toolsPanel).toHaveClass(/is-collapsed/);

    // Verify expand rail button is visible
    const expandRail = page.locator('.panel-rail-button[data-expand="tools"]');
    await expect(expandRail).toBeVisible();

    // Click expand to restore
    await expandRail.click();
    await page.waitForTimeout(300);
    await expect(toolsPanel).not.toHaveClass(/is-collapsed/);
  });

  test('6.3 Resize panels', async ({ page }) => {
    await createNotebook(page);
    await expect(page.locator('#scene-chat')).toBeVisible();

    // Get initial width of the left panel
    const sourcesPanel = page.locator('.chat-panel[data-panel="sources"]');
    const initialBox = await sourcesPanel.boundingBox();
    const initialWidth = initialBox ? initialBox.width : 320;

    // Get the resizer position
    const resizer = page.locator('.chat-resizer[data-resize="left"]');
    await expect(resizer).toBeVisible();
    const resizerBox = await resizer.boundingBox();

    // Simulate pointerdown → pointermove → pointerup sequence
    const startX = resizerBox.x + resizerBox.width / 2;
    const startY = resizerBox.y + resizerBox.height / 2;
    const moveDelta = 80; // pixels to drag right

    // Pointer down
    await page.mouse.move(startX, startY);
    await page.mouse.down();

    // Move right (expand)
    await page.mouse.move(startX + moveDelta, startY, { steps: 10 });
    await page.waitForTimeout(100);

    // Release
    await page.mouse.up();
    await page.waitForTimeout(300);

    // Verify left panel width changed
    const newBox = await sourcesPanel.boundingBox();
    const newWidth = newBox ? newBox.width : 0;
    expect(newWidth).toBeGreaterThan(initialWidth);

    // Check CSS variable --left-user-width updated on the chat shell
    const chatShell = page.locator('.chat-shell');
    const computedStyle = await page.evaluate(() => {
      const shell = document.querySelector('.chat-shell');
      return shell ? getComputedStyle(shell).getPropertyValue('--left-user-width').trim() : '';
    });
    // The value should reflect the new pixel count (initial + delta)
    const expectedWidth = initialWidth + moveDelta;
    // Allow tolerance of ±5px
    expect(parseInt(computedStyle)).toBeGreaterThanOrEqual(expectedWidth - 5);
    expect(parseInt(computedStyle)).toBeLessThanOrEqual(expectedWidth + 5);
  });

  test('6.4 Double-click resizer reset', async ({ page }) => {
    await createNotebook(page);
    await expect(page.locator('#scene-chat')).toBeVisible();

    // Get the resizer
    const resizer = page.locator('.chat-resizer[data-resize="left"]');
    await expect(resizer).toBeVisible();
    const resizerBox = await resizer.boundingBox();

    // Get initial width
    const sourcesPanel = page.locator('.chat-panel[data-panel="sources"]');
    const initialBox = await sourcesPanel.boundingBox();
    const initialWidth = initialBox ? initialBox.width : 320;

    // Resize: drag right by 80px
    const startX = resizerBox.x + resizerBox.width / 2;
    const startY = resizerBox.y + resizerBox.height / 2;
    const moveDelta = 80;

    await page.mouse.move(startX, startY);
    await page.mouse.down();
    await page.mouse.move(startX + moveDelta, startY, { steps: 10 });
    await page.mouse.up();
    await page.waitForTimeout(300);

    // Verify width changed
    const resizedBox = await sourcesPanel.boundingBox();
    const resizedWidth = resizedBox ? resizedBox.width : 0;
    expect(resizedWidth).toBeGreaterThan(initialWidth);

    // Double-click the resizer to reset
    await resizer.dblclick();
    await page.waitForTimeout(500);

    // Verify panel width reset to default
    const resetBox = await sourcesPanel.boundingBox();
    const resetWidth = resetBox ? resetBox.width : 0;
    expect(resetWidth).toBeLessThan(resizedWidth);
    // Should be back to ~320px (the default --left-user-width)
    expect(resetWidth).toBeGreaterThanOrEqual(initialWidth - 10);
  });

  test('6.5 Save conversation', async ({ page }) => {
    await createNotebook(page);
    await expect(page.locator('#scene-chat')).toBeVisible();

    // Send a chat message first (so there's content to save)
    const textarea = page.locator('#chatPrompt');
    await expect(textarea).toBeVisible();
    await textarea.fill('What is the capital of France?');
    await page.click('.send-button');

    // Wait for message to appear
    await expect(page.locator('.message.user').first()).toBeVisible({ timeout: 5000 });
    await page.waitForTimeout(500);

    // Click the "Save" button (has bookmark_add icon or "Save" text)
    const saveBtn = page.locator('[data-action="save-conversation"]');
    await expect(saveBtn).toBeVisible();
    await saveBtn.click();

    // Wait for any feedback
    await page.waitForTimeout(800);

    // Verify no console errors occurred
    const errorCount = await page.evaluate(() => {
      return window.__testErrors ? window.__testErrors.length : 0;
    });
    expect(errorCount).toBe(0);
  });

  test('6.6 Pin message', async ({ page }) => {
    await createNotebook(page);
    await expect(page.locator('#scene-chat')).toBeVisible();

    // Send a chat message
    const textarea = page.locator('#chatPrompt');
    await textarea.fill('Hello world');
    await page.click('.send-button');

    // Wait for user message
    await expect(page.locator('.message.user').first()).toBeVisible({ timeout: 5000 });
    await page.waitForTimeout(1000);

    // Hover over a message
    const userMessage = page.locator('.message.user').first();
    await userMessage.hover();
    await page.waitForTimeout(200);

    // Click the pin icon (push_pin or "Pin")
    const pinBtn = userMessage.locator('.message-action', { has: page.locator('.material-icons', { hasText: 'push_pin' }) });
    await expect(pinBtn).toBeVisible();

    // Track errors
    const errors = [];
    page.on('console', msg => {
      if (msg.type() === 'error') errors.push(msg.text());
    });

    await pinBtn.click();
    await page.waitForTimeout(800);

    // Verify no console errors
    expect(errors.filter(e => !e.includes('favicon'))).toHaveLength(0);
  });

  test('6.7 Conversation persistence', async ({ page }) => {
    await createNotebook(page);
    await expect(page.locator('#scene-chat')).toBeVisible();

    // Get the notebook title
    const title = await page.locator('.chat-title').textContent();

    // Send a chat message
    const textarea = page.locator('#chatPrompt');
    await textarea.fill('Test message for persistence');
    await page.click('.send-button');

    // Wait for message to appear
    await expect(page.locator('.message.user').first()).toBeVisible({ timeout: 5000 });
    await page.waitForTimeout(300);

    // Navigate back to dashboard
    const backBtn = page.locator('.chat-back-button');
    await expect(backBtn).toBeVisible();
    await backBtn.click();

    // Wait for dashboard
    await expect(page.locator('#scene-dashboard')).toBeVisible({ timeout: 5000 });

    // Reopen the same notebook
    await openNotebook(page, title);

    // Wait for chat scene
    await expect(page.locator('#scene-chat')).toBeVisible({ timeout: 5000 });

    // Verify previous conversation is loaded
    await page.waitForTimeout(1000); // Allow messages to load
    const messages = page.locator('.message, .ai-response');
    const count = await messages.count();
    expect(count).toBeGreaterThan(1); // Should have the initial greeting + at least one user message
  });
});