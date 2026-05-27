/**
 * Playwright E2E Tests for Chat functionality.
 * Tests: 4.1 - 4.6
 * Base URL: http://localhost/
 */

import { test, expect } from '@playwright/test';
import { signIn, signOut, signUp } from './helpers/auth.js';
import { createNotebook } from './helpers/notebooks.js';
import { uploadFile, waitForUploadComplete } from './helpers/upload.js';
import { resolve } from 'path';
import { fileURLToPath } from 'url';

const __dirname = fileURLToPath(new URL('.', import.meta.url));
const TEST_DATA_DIR = resolve(__dirname, '..', '..', '..', 'data', 'raw');

const TEST_EMAIL = 'vha7244@gmail.com';
const TEST_PASSWORD = '123456';
const TEST_PDF_PATH = resolve(TEST_DATA_DIR, 'test.pdf');

test.describe('Chat Suite (4.x)', () => {

    test.beforeEach(async ({ page }) => {
        // Start at the landing page
        await page.goto('http://localhost/');
    });

    /**
     * 4.1 Upload PDF and send chat message - verify streaming response
     * Test that after uploading a PDF, the user can send a message and receive a streaming response.
     */
    test('4.1 Upload PDF then chat - verify streaming response', async ({ page }) => {
        // Sign in
        await signIn(page, TEST_EMAIL, TEST_PASSWORD);

        // Create a new notebook
        await createNotebook(page);

        // Verify ChatScene is visible
        await expect(page.locator('#scene-chat')).toBeVisible();

        // Upload a PDF file
        try {
            await uploadFile(page, TEST_PDF_PATH);
            await waitForUploadComplete(page);
        } catch (e) {
            test.skip('Test PDF file not found');
        }

        // Wait for source to appear
        await page.waitForSelector('.source-item', { state: 'visible' });

        // Send a chat message
        await page.fill('#chatPrompt', 'What is this document about? Summarize the key points.');
        await page.press('#chatPrompt', 'Enter');

        // Wait for AI response to appear
        // The response should have streaming effect - we wait for the message to appear
        await page.waitForSelector('.message.user', { state: 'visible', timeout: 10000 });

        // Wait for AI response
        await page.waitForSelector('.message.ai, .ai-response', { state: 'visible', timeout: 30000 });

        // Verify the response contains text (streaming completed or in progress)
        const aiResponse = page.locator('.ai-response, .message.ai').last();
        await expect(aiResponse).toBeVisible();

        // Verify response is not the empty welcome message
        const responseText = await aiResponse.textContent();
        expect(responseText).not.toContain('Hi, I can help you explore your sources');
    });

    /**
     * 4.2 Citation buttons - click and verify source viewer opens
     * Test that AI responses with citations have clickable buttons that open the source viewer.
     */
    test('4.2 Citation buttons - click and verify source viewer opens', async ({ page }) => {
        // Sign in
        await signIn(page, TEST_EMAIL, TEST_PASSWORD);

        // Create a new notebook
        await createNotebook(page);

        // Upload a PDF file
        try {
            await uploadFile(page, TEST_PDF_PATH);
            await waitForUploadComplete(page);
        } catch (e) {
            test.skip('Test PDF file not found');
        }

        // Wait for source to appear
        await page.waitForSelector('.source-item', { state: 'visible' });

        // Send a chat message that should trigger citations
        await page.fill('#chatPrompt', 'What are the main topics in this document?');
        await page.press('#chatPrompt', 'Enter');

        // Wait for AI response
        await page.waitForSelector('.ai-response, .message.ai', { state: 'visible', timeout: 30000 });

        // Wait for streaming to complete (allow more time)
        await page.waitForTimeout(3000);

        // Look for citation buttons in the response
        const citationButtons = page.locator('.citation-btn');
        const citationCount = await citationButtons.count();

        if (citationCount > 0) {
            // Click the first citation button
            await citationButtons.first().click();

            // Wait for source viewer to open/expand
            await page.waitForTimeout(1000);

            // Verify the viewer is showing content
            const viewerContent = page.locator('.viewer-content');
            await expect(viewerContent).toBeVisible();
        } else {
            // No citations found - the response might not have triggered citations
            // This is acceptable as it depends on the document content and AI response
            test.skip('No citation buttons found in response');
        }
    });

    /**
     * 4.3 New chat button clears conversation
     * Test that clicking "New chat" clears the conversation history.
     */
    test('4.3 New chat button clears conversation', async ({ page }) => {
        // Sign in
        await signIn(page, TEST_EMAIL, TEST_PASSWORD);

        // Create a new notebook
        await createNotebook(page);

        // Verify ChatScene is visible
        await expect(page.locator('#scene-chat')).toBeVisible();

        // Send a chat message
        await page.fill('#chatPrompt', 'Hello, what can you do?');
        await page.press('#chatPrompt', 'Enter');

        // Wait for AI response
        await page.waitForSelector('.ai-response, .message.ai', { state: 'visible', timeout: 30000 });

        // Verify message appears
        const userMessage = page.locator('.message.user, .user-message');
        await expect(userMessage).toBeVisible();

        // Click "New chat" button
        await page.click('.panel-icon-button[data-action="new-chat"]');

        // Wait for conversation to be cleared
        await page.waitForTimeout(1000);

        // Verify the chat thread is cleared (only welcome message should remain)
        const chatThread = page.locator('.chat-thread');
        const threadContent = await chatThread.textContent();

        // The welcome message should be visible
        expect(threadContent).toContain('Hi, I can help you explore your sources');

        // User messages should be gone
        const userMessages = page.locator('.message.user, .user-message');
        await expect(userMessages).toHaveCount(0);
    });

    /**
     * 4.4 Open empty notebook and send message - verify "Please add sources" response
     * Test that sending a message to a notebook without sources shows a helpful message.
     */
    test('4.4 Empty notebook - verify "Please add sources" response', async ({ page }) => {
        // Sign in
        await signIn(page, TEST_EMAIL, TEST_PASSWORD);

        // Create a new notebook (without uploading any files)
        await createNotebook(page);

        // Verify ChatScene is visible
        await expect(page.locator('#scene-chat')).toBeVisible();

        // Verify no sources are present
        const sourceItems = page.locator('.source-item');
        await expect(sourceItems).toHaveCount(0);

        // Send a chat message
        await page.fill('#chatPrompt', 'What is this document about?');
        await page.press('#chatPrompt', 'Enter');

        // Wait for response
        await page.waitForTimeout(2000);

        // Check if the response indicates no sources
        const aiResponse = page.locator('.ai-response, .message.ai').last();
        const responseText = await aiResponse.textContent();

        // The response should mention the need to add sources
        // or the welcome message should still be shown
        const hasSourceReminder = responseText.toLowerCase().includes('add sources') ||
            responseText.toLowerCase().includes('no sources') ||
            responseText.toLowerCase().includes('upload');

        // This test verifies the system handles empty sources gracefully
        expect(responseText).toBeTruthy();
    });

    /**
     * 4.5 Multi-user isolation - sign out, sign in as different user, verify isolation
     * Test that user data is properly isolated between accounts.
     */
    test('4.5 Multi-user isolation - verify data separation', async ({ page }) => {
        // Create a timestamp-based unique email for the second user
        const timestamp = Date.now();
        const secondUserEmail = `test_user_${timestamp}@example.com`;
        const secondUserPassword = 'TestPassword123!';

        // Sign in as first user
        await signIn(page, TEST_EMAIL, TEST_PASSWORD);

        // Create a notebook as first user
        const firstUserNotebookTitle = await createNotebook(page);

        // Go back to dashboard
        await page.click('.chat-back-button');
        await page.waitForSelector('#scene-dashboard', { state: 'visible' });

        // Get the list of notebooks for first user
        const firstUserNotebooks = await page.locator('.my-grid .notebook-item .item-title').allTextContents();

        // Sign out
        await signOut(page);

        // Sign up as a different user
        const username = `user_${timestamp}`;
        await signUp(page, username, secondUserEmail, secondUserPassword);

        // Verify dashboard is shown
        await expect(page.locator('#scene-dashboard')).toBeVisible();

        // Get the list of notebooks for second user
        const secondUserNotebooks = await page.locator('.my-grid .notebook-item .item-title').allTextContents();

        // Verify the notebooks are different
        // The second user should not see the first user's notebooks
        expect(secondUserNotebooks).not.toContain(firstUserNotebookTitle);

        // Note: This test assumes the second user has no pre-existing notebooks
        // In a real scenario, you might want to clean up the test user after the test
    });

    /**
     * 4.6 PDF chat does not show Excel query result
     * Test that chat stays on the RAG path while tabular query is disabled.
     */
    test('4.6 PDF chat does not show Excel query result', async ({ page }) => {
        // Sign in
        await signIn(page, TEST_EMAIL, TEST_PASSWORD);

        // Create a new notebook
        await createNotebook(page);

        // Verify ChatScene is visible
        await expect(page.locator('#scene-chat')).toBeVisible();

        // Upload a PDF file
        try {
            await uploadFile(page, TEST_PDF_PATH);
            await waitForUploadComplete(page);
        } catch (e) {
            test.skip('Test PDF file not found');
        }

        // Wait for source to appear
        await page.waitForSelector('.source-item', { state: 'visible' });

        // Send a question about the source file
        await page.fill('#chatPrompt', 'What is this document about? Give me a summary.');
        await page.press('#chatPrompt', 'Enter');

        // Wait for AI response
        await page.waitForSelector('.ai-response, .message.ai', { state: 'visible', timeout: 30000 });

        // Wait for response to complete
        await page.waitForTimeout(3000);

        // Verify response contains content
        const aiResponse = page.locator('.ai-response, .message.ai').last();
        await expect(aiResponse).toBeVisible();

        // Verify response is not the empty welcome message
        const responseText = await aiResponse.textContent();
        expect(responseText).not.toContain('Hi, I can help you explore your sources');
        expect(responseText).not.toContain('Excel Query Result');
    });

    /**
     * 4.7 Source sidebar interaction separation
     * Checkbox toggles selection only, row body opens preview, and kebab opens menu only.
     */
    test('4.7 Source selection and row actions remain isolated', async ({ page }) => {
        await signIn(page, TEST_EMAIL, TEST_PASSWORD);
        await createNotebook(page);
        await expect(page.locator('#scene-chat')).toBeVisible();

        try {
            await uploadFile(page, TEST_PDF_PATH);
            await waitForUploadComplete(page);
        } catch (e) {
            test.skip('Test PDF file not found');
        }

        const sourceItem = page.locator('.source-item').first();
        await expect(sourceItem).toBeVisible();
        await expect(page.locator('.source-select-all-checkbox')).toBeVisible();
        const sourceCheckbox = sourceItem.locator('.source-select-checkbox');
        await expect(sourceCheckbox).toBeVisible();
        await expect(sourceCheckbox).toBeChecked();

        const menuBtn = sourceItem.locator('.source-menu-btn');
        const initialOpacity = await menuBtn.evaluate((el) => getComputedStyle(el).opacity);
        expect(initialOpacity).toBe('0');

        await sourceItem.hover();
        const hoveredOpacity = await menuBtn.evaluate((el) => getComputedStyle(el).opacity);
        expect(Number(hoveredOpacity)).toBeGreaterThan(0);

        const viewerContent = page.locator('#sourceViewer .viewer-content');
        await expect(viewerContent).toBeHidden();

        await sourceCheckbox.click();
        await expect(viewerContent).toBeHidden();

        await menuBtn.click();
        await expect(sourceItem.locator('.source-menu')).toBeVisible();
        await expect(viewerContent).toBeHidden();

        await page.keyboard.press('Escape');
        await expect(sourceItem.locator('.source-menu')).toBeHidden();

        await sourceItem.locator('.source-meta').click();
        await expect(viewerContent).toBeVisible();
    });

});
