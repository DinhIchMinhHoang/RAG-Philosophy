import fs from 'node:fs/promises';
import path from 'node:path';
import { createRequire } from 'node:module';

const require = createRequire(import.meta.url);
const { chromium } = require('C:/Users/vha72/AppData/Local/npm-cache/_npx/e41f203b7505f1fb/node_modules/playwright');

const ROOT = process.cwd();
const RUN_ID = new Date().toISOString().replace(/[-:]/g, '').replace(/\..+$/, '').replace('T', '-');
const OUT_DIR = path.join(ROOT, 'e2e-artifacts', RUN_ID);
const FILE_PATH = path.join(ROOT, 'data', 'raw', 'Deep Learning (243-247).pdf');
const CHROME_PATH = 'C:/Users/vha72/AppData/Local/ms-playwright/chromium-1223/chrome-win64/chrome.exe';
const BASE_URL = 'http://localhost';
const EMAIL = 'vha7244@gmail.com';
const PASSWORD = '123456';

const timings = [];
const failedRequests = [];
const badTargetRequests = [];
const consoleErrors = [];
const screenshots = [];
const chatResults = [];

function now() {
  return performance.now();
}

function elapsed(start) {
  return Math.round(performance.now() - start);
}

function addTiming(operation, durationMs, status, notes = '') {
  timings.push({ operation, duration_ms: durationMs, status, notes });
}

function parseSse(body) {
  const events = [];
  for (const block of String(body || '').split(/\n\n+/)) {
    const line = block.split('\n').find((value) => value.trim().startsWith('data: '));
    if (!line) continue;
    try {
      events.push(JSON.parse(line.trim().slice(6)));
    } catch {
      events.push({ parse_error: line.trim() });
    }
  }
  return events;
}

async function saveScreenshot(page, name) {
  const file = path.join(OUT_DIR, `${name}.png`);
  await page.screenshot({ path: file, fullPage: true });
  screenshots.push(file);
  return file;
}

async function waitForChatDom(page, beforeCount, timeoutMs = 180000) {
  const start = now();
  let firstTextMs = null;
  let finalText = '';
  await page.waitForFunction(
    ({ beforeCount }) => {
      const messages = Array.from(document.querySelectorAll('#scene-chat .ai-response'));
      if (messages.length <= beforeCount) return false;
      const latest = messages[messages.length - 1];
      const text = latest.querySelector('.message-text')?.innerText?.trim() || '';
      return text.length > 0;
    },
    { beforeCount },
    { timeout: timeoutMs }
  );
  firstTextMs = elapsed(start);

  await page.waitForFunction(
    ({ beforeCount }) => {
      const messages = Array.from(document.querySelectorAll('#scene-chat .ai-response'));
      if (messages.length <= beforeCount) return false;
      const latest = messages[messages.length - 1];
      return !latest.classList.contains('streaming');
    },
    { beforeCount },
    { timeout: timeoutMs }
  );

  finalText = await page.evaluate(() => {
    const messages = Array.from(document.querySelectorAll('#scene-chat .ai-response'));
    const latest = messages[messages.length - 1];
    return latest?.querySelector('.message-text')?.innerText?.trim() || '';
  });
  return { firstTextMs, totalMs: elapsed(start), finalText };
}

async function sendChat(page, label, message, timeoutMs = 180000) {
  const beforeCount = await page.locator('#scene-chat .ai-response').count();
  const start = now();
  const responsePromise = page.waitForResponse(
    (response) => response.url().includes('/api/chat/stream') && response.request().method() === 'POST',
    { timeout: timeoutMs }
  );
  await page.fill('#chatPrompt', message);
  await page.press('#chatPrompt', 'Enter');
  const response = await responsePromise;
  const status = response.status();
  let body = '';
  try {
    body = await response.text();
  } catch (error) {
    body = `<<response body unavailable: ${error.message}>>`;
  }
  const dom = await waitForChatDom(page, beforeCount, timeoutMs);
  const events = parseSse(body);
  const finalEvent = events.find((event) => event.done) || events[events.length - 1] || null;
  const result = {
    label,
    endpoint: response.url(),
    status,
    request_duration_ms: elapsed(start),
    first_token_latency_ms: dom.firstTextMs,
    total_duration_ms: dom.totalMs,
    final_event: finalEvent,
    response_text: dom.finalText,
  };
  chatResults.push(result);
  addTiming(`${label} - first token/text`, dom.firstTextMs, status, response.url());
  addTiming(`${label} - total`, dom.totalMs, status, finalEvent?.type || '');
  return result;
}

async function fetchInPage(page, url, options = {}) {
  return await page.evaluate(
    async ({ url, options }) => {
      const headers = { ...(options.headers || {}) };
      const token = localStorage.getItem('accessToken');
      if (token) headers.Authorization = `Bearer ${token}`;
      if (options.body && !headers['Content-Type']) headers['Content-Type'] = 'application/json';
      const response = await fetch(url, { ...options, headers });
      const text = await response.text();
      let json = null;
      try {
        json = text ? JSON.parse(text) : null;
      } catch {
        json = null;
      }
      return { status: response.status, ok: response.ok, text, json };
    },
    { url, options }
  );
}

async function main() {
  await fs.mkdir(OUT_DIR, { recursive: true });
  const browser = await chromium.launch({
    headless: true,
    executablePath: CHROME_PATH,
    args: ['--no-sandbox'],
  });
  const context = await browser.newContext({ viewport: { width: 1440, height: 1000 } });
  await context.addInitScript(() => localStorage.clear());
  const page = await context.newPage();

  page.on('console', (message) => {
    if (message.type() === 'error') consoleErrors.push({ text: message.text(), location: message.location() });
  });
  page.on('request', (request) => {
    const url = request.url();
    if (url.startsWith('http://127.0.0.1:8000') || url.startsWith('http://localhost:8000')) {
      badTargetRequests.push({ method: request.method(), url });
    }
  });
  page.on('requestfailed', (request) => {
    failedRequests.push({
      method: request.method(),
      url: request.url(),
      failure: request.failure()?.errorText || 'unknown',
    });
  });
  page.on('response', async (response) => {
    const status = response.status();
    const url = response.url();
    if (status >= 400 && url.startsWith(BASE_URL)) {
      let body = '';
      try {
        body = await response.text();
      } catch {
        body = '';
      }
      failedRequests.push({ method: response.request().method(), url, status, body });
    }
  });

  const pageStart = now();
  await page.goto(BASE_URL, { waitUntil: 'domcontentloaded', timeout: 60000 });
  addTiming('Page load', elapsed(pageStart), 'ok');
  await page.waitForTimeout(800);

  const loginStart = now();
  const loginResponsePromise = page.waitForResponse(
    (response) => response.url().includes('/api/login') && response.request().method() === 'POST',
    { timeout: 60000 }
  );
  await page.click('button[data-scene="signin"]');
  await page.fill('#signin-email', EMAIL);
  await page.fill('#signin-password', PASSWORD);
  await page.click('#signin-form button[type="submit"]');
  const loginResponse = await loginResponsePromise;
  await page.waitForSelector('#scene-dashboard', { state: 'visible', timeout: 60000 });
  addTiming('Login', elapsed(loginStart), loginResponse.status(), loginResponse.url());
  await saveScreenshot(page, 'after-login');

  const title = `E2E Test Notebook - ${RUN_ID}`;
  const createStart = now();
  const createResult = await fetchInPage(page, '/api/notebooks', {
    method: 'POST',
    body: JSON.stringify({ title, is_community: false }),
  });
  if (!createResult.ok) throw new Error(`Create notebook failed: ${createResult.status} ${createResult.text}`);
  const notebook = createResult.json;
  await page.evaluate(() => document.dispatchEvent(new CustomEvent('auth:changed')));
  await page.waitForSelector(`.notebook-item[data-notebook-id="${notebook.id}"]`, { timeout: 60000 });
  addTiming('Create notebook', elapsed(createStart), createResult.status, `id=${notebook.id}`);
  await saveScreenshot(page, 'after-notebook-create');

  await page.click(`.notebook-item[data-notebook-id="${notebook.id}"]`);
  await page.waitForSelector('#scene-chat', { state: 'visible', timeout: 60000 });
  await saveScreenshot(page, 'notebook-opened');

  await sendChat(page, 'Chat before upload', 'What is this notebook about?', 120000);
  await saveScreenshot(page, 'after-pre-upload-chat');

  const uploadStart = now();
  const uploadResponsePromise = page.waitForResponse(
    (response) => response.url().includes('/api/documents') && response.request().method() === 'POST',
    { timeout: 120000 }
  );
  await page.setInputFiles('#sourceFileInput', FILE_PATH);
  const uploadResponse = await uploadResponsePromise;
  const uploadStatus = uploadResponse.status();
  const uploadBody = await uploadResponse.json().catch(async () => ({ text: await uploadResponse.text().catch(() => '') }));
  addTiming('File upload request', elapsed(uploadStart), uploadStatus, `job_id=${uploadBody.job_id || ''}`);
  await page.getByText(path.basename(FILE_PATH)).waitFor({ timeout: 60000 }).catch(() => {});
  addTiming('File visible in UI', elapsed(uploadStart), 'ok');
  await saveScreenshot(page, 'after-upload-request');

  let ingestStartedMs = null;
  let ingestCompletedMs = null;
  const progressUpdates = [];
  if (uploadBody.job_id) {
    const ingestStart = now();
    for (let attempt = 0; attempt < 180; attempt += 1) {
      const jobResult = await fetchInPage(page, `/api/jobs/${encodeURIComponent(uploadBody.job_id)}`, { method: 'GET' });
      const job = jobResult.json || {};
      progressUpdates.push({
        status: job.status,
        stage: job.stage,
        progress_pct: job.progress_pct,
        error_message: job.error_message || null,
      });
      if (job.status && job.status !== 'queued' && ingestStartedMs === null) {
        ingestStartedMs = elapsed(ingestStart);
        addTiming('Ingest started', ingestStartedMs, job.status, job.stage || '');
      }
      if (job.status === 'succeeded') {
        ingestCompletedMs = elapsed(ingestStart);
        addTiming('Ingest completed', ingestCompletedMs, job.status, job.stage || '');
        break;
      }
      if (job.status === 'failed') {
        addTiming('Ingest completed', elapsed(ingestStart), job.status, job.error_message || '');
        throw new Error(`Ingest failed: ${job.error_message || JSON.stringify(job)}`);
      }
      await page.waitForTimeout(2000);
    }
    if (ingestCompletedMs === null) throw new Error(`Ingest did not complete for job ${uploadBody.job_id}`);
  }
  await saveScreenshot(page, 'after-ingest-complete');

  await sendChat(page, 'Chat after upload - summary', 'Summarize this document.', 240000);
  await saveScreenshot(page, 'after-summary-chat');
  await sendChat(page, 'Chat after upload - retrieval', 'What is the document mainly about?', 240000);
  await sendChat(page, 'Follow-up key points', 'What are the key points?', 240000);
  await sendChat(page, 'Follow-up explain second', 'Can you explain the second one more clearly?', 240000);
  await saveScreenshot(page, 'after-follow-up-chat');

  const cleanup = await fetchInPage(page, `/api/notebooks/${encodeURIComponent(notebook.id)}`, { method: 'DELETE' });
  addTiming('Cleanup notebook', 0, cleanup.status, `id=${notebook.id}`);

  const report = {
    run_id: RUN_ID,
    notebook,
    upload: uploadBody,
    progress_updates: progressUpdates,
    timings,
    chat_results: chatResults,
    screenshots,
    console_errors: consoleErrors,
    failed_requests: failedRequests,
    bad_target_requests: badTargetRequests,
  };
  await fs.writeFile(path.join(OUT_DIR, 'report.json'), JSON.stringify(report, null, 2));
  await browser.close();
  console.log(JSON.stringify(report, null, 2));
}

main().catch(async (error) => {
  const failure = {
    run_id: RUN_ID,
    error: error.stack || error.message,
    timings,
    chat_results: chatResults,
    screenshots,
    console_errors: consoleErrors,
    failed_requests: failedRequests,
    bad_target_requests: badTargetRequests,
  };
  await fs.mkdir(OUT_DIR, { recursive: true });
  await fs.writeFile(path.join(OUT_DIR, 'failure.json'), JSON.stringify(failure, null, 2));
  console.error(JSON.stringify(failure, null, 2));
  process.exit(1);
});
