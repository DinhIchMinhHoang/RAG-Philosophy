# Playwright E2E Test Plan — RAG Philosophy (Lumina)

## Overview

End-to-end browser tests for the Lumina RAG application covering authentication, notebook management, supported document upload + deduplication, chat/RAG streaming, and UI interactions.

**Scope:** Auth, Notebooks, Upload, Chat, Dashboard UI, Chat UX, Edge Cases
**Excluded:** Password Reset, Admin Panel

**Test Structure:**
```
frontend/tests/playwright/
├── auth.spec.js          # P0: Sign In, Sign Up, Logout, Auth guard
├── notebooks.spec.js     # P0: CRUD Notebook
├── upload.spec.js        # P0: Upload formats + dedup + replace
├── chat.spec.js          # P0: Chat streaming, citations, multi-user
├── dashboard-ui.spec.js  # P1: Grid/List, Cover image, Show All
├── chat-ux.spec.js       # P1: Panel resize, collapse, save, pin
├── edge-cases.spec.js    # P2: Multi-file upload, refresh, abort
└── helpers/
    ├── auth.js           # signIn(), signUp(), signOut()
    ├── notebooks.js      # createNotebook(), openNotebook(), deleteNotebook()
    └── upload.js         # uploadFile(), waitForUploadComplete()
```

## Priority Levels

- **P0:** Critical path — must pass before any merge
- **P1:** Important — should pass, test core UX
- **P2:** Edge cases — nice to have

---

## P0: Critical Path Tests

### 1. Authentication (`auth.spec.js`)

| # | Test | Steps | Expected |
|---|---|---|---|
| 1.1 | Sign In success | Landing → click "Sign In" → fill email + password → submit | Redirect to dashboard, navbar shows account icon |
| 1.2 | Sign In fail | Wrong email or password | `.form-error` displayed, password field cleared |
| 1.3 | Sign Up success | Landing → "Sign Up" → username + email + pw + confirm → submit | Redirect to dashboard |
| 1.4 | Sign Up validation | Mismatched passwords, invalid email, password < 6 chars | `.form-field-error` shown, form not submitted |
| 1.5 | Logout | Account page → "Log out" button | Token cleared, redirect to landing page |
| 1.6 | Auth guard | Navigate to dashboard URL without signing in | Redirect to landing page |

### 2. Notebook CRUD (`notebooks.spec.js`)

| # | Test | Steps | Expected |
|---|---|---|---|
| 2.1 | Create notebook | Dashboard → "Create new notebook" | "Untitled notebook" appears in My notebooks grid |
| 2.2 | Open notebook | Click notebook item | Navigate to ChatScene, topbar shows notebook title |
| 2.3 | Rename notebook | More menu (⋮) → Rename → prompt → enter new name → OK | Title updates on both dashboard and chat topbar |
| 2.4 | Delete notebook | More menu → Delete → confirm dialog → OK | Notebook disappears from grid. If currently open → redirect to dashboard |
| 2.5 | Delete notebook with source | Notebook containing supported source file → delete | Verify: object storage cleaned, Qdrant vectors deleted, metadata removed |

### 3. Document Upload (`upload.spec.js`)

| # | Test | File | Steps | Expected |
|---|---|---|---|---|
| 3.1 | Upload PDF | `.pdf` | Add source → choose file | Status "Ready", shows `N pages, M chunks` |
| 3.2 | Upload DOCX | `.docx` | Add source → choose file | Status "Ready" |
| 3.3 | Upload HTML | `.html` | Add source → choose file | Status "Ready" |
| 3.4 | Upload MD | `.md` | Add source → choose file | Status "Ready" |
| 3.5 | Reject XLSX | `.xlsx` | Add source → choose file | Error: "Unsupported format"; no backend upload request |
| 3.6 | Reject CSV | `.csv` | Add source → choose file | Error: "Unsupported format"; no backend upload request |
| 3.7 | **Dedup: 409 block** | Same file, same notebook | Upload already-existing file | Confirm modal "File already exists" with 2 buttons |
| 3.8 | **Dedup: Cancel** | — | Modal → click "No" | Uploading item removed from source list, existing file unchanged |
| 3.9 | **Dedup: Replace** | — | Modal → click "Yes" | File replaced, `document_id` preserved, status "Ready" |
| 3.10 | **Dedup: Different notebook** | Same file, different notebook | Upload same file to another notebook | NOT blocked, new document created |
| 3.11 | Delete source | — | Source menu → Delete → confirm | File removed from list, cleanup: storage + vectors; legacy Excel tables are cleaned up only when deleting old tabular documents |
| 3.12 | Rename source | — | Source menu → Rename → inline edit → Enter | Filename updated in source list |
| 3.13 | Drag & drop upload | PDF | Drag file into `.source-drop` zone | Upload succeeds |
| 3.14 | Reject unsupported format | `.exe` | Upload | Error: "Unsupported format" |
| 3.15 | Reject file too large | `>20MB` | Upload | Error: "File too large" |
| 3.16 | Reject empty file | 0 bytes | Upload | Error: "Uploaded file is empty" |

### 4. Chat / RAG (`chat.spec.js`)

| # | Test | Steps | Expected |
|---|---|---|---|
| 4.1 | Chat basic | Notebook with sources → type question → Enter | AI streams response with markdown rendering and citations |
| 4.2 | Citation click | Click `[C1]` in AI response | Source Viewer opens to correct file + page |
| 4.3 | New chat | Click "New chat" button | Conversation cleared, welcome message shown |
| 4.4 | Empty notebook | Notebook with no files → send message | Response: "Please add sources to this notebook" |
| 4.5 | Multi-user isolation | Sign out user A → sign in user B → open B's notebook | Only user B's data visible, user A's data not accessible |
| 4.6 | Chat ignores legacy Excel source | Notebook with PDF + legacy Excel record → ask PDF-related question | Response uses RAG context/citations only; no Excel query result section |

---

## P1: Important Tests

### 5. Dashboard UI (`dashboard-ui.spec.js`)

| # | Test | Steps | Expected |
|---|---|---|---|
| 5.1 | Grid ↔ List toggle | Click List → click Grid | Layout changes between grid and list views |
| 5.2 | Cover image upload | More menu → Change image → Upload tab → choose image → Apply | Notebook cover updated |
| 5.3 | Cover color | More menu → Change image → Color tab → pick color → Apply | Notebook cover color updated |
| 5.4 | Show All | Dashboard → "Show all" button | Dedicated scene showing all notebooks |

### 6. Chat UX (`chat-ux.spec.js`)

| # | Test | Steps | Expected |
|---|---|---|---|
| 6.1 | Collapse Sources | Click left chevron | Sources panel collapses, rail icon shown |
| 6.2 | Collapse Viewer | Click right chevron | Source Viewer panel collapses |
| 6.3 | Resize panels | Drag resizer handle | Panel width changes, never below 200px |
| 6.4 | Double-click reset | Double-click resizer | Panels reset to default width |
| 6.5 | Save conversation | Click "Save" button | Conversation text saved to notes |
| 6.6 | Pin message | Hover message → click pin icon | Individual message saved |
| 6.7 | Conversation persistence | Chat → leave notebook → reopen | Previous conversation loaded from cache |

---

## P2: Edge Cases (`edge-cases.spec.js`)

| # | Test | Steps | Expected |
|---|---|---|---|
| 7.1 | Upload multiple files | Select 5 files at once | All upload sequentially, all reach "Ready" |
| 7.2 | Refresh during chat | F5 while streaming response | Application recovers, no corrupted state |
| 7.3 | Unsupported Excel upload | Upload `.xlsx` | Error: "Unsupported format"; file is not sent to backend |
| 7.4 | New note (no API) | Click "New note" → type text → OK | Note appears in source list |
| 7.5 | Stream abort on navigate | While streaming → navigate to another notebook | Stream aborted cleanly, no errors |

---

## Helper Functions

### `helpers/auth.js`
```js
// signIn(page, email, password) — complete sign in flow, returns void
// signUp(page, username, email, password) — complete sign up flow
// signOut(page) — sign out and verify redirect to landing
```

### `helpers/notebooks.js`
```js
// createNotebook(page) — create new notebook, returns notebook title
// openNotebook(page, title) — click notebook to enter chat scene
// deleteNotebook(page, title) — delete notebook via more menu
// openMoreMenu(page, notebookTitle) — open the ⋮ context menu
```

### `helpers/upload.js`
```js
// uploadFile(page, filePath) — upload file via file chooser, return { documentId, result }
// waitForUploadComplete(page, timeoutMs) — wait until source shows "Ready"
// getSourceItems(page) — return all .source-item DOM elements
```

---

## Test Fixtures

Test files needed in a fixtures directory:
- `test.pdf` — simple PDF (1-2 pages)
- `test.docx` — simple DOCX document
- `test.html` — simple HTML page
- `test.md` — simple Markdown file
- `test.xlsx` — Excel file used only for unsupported-format checks while tabular ingest is disabled
- `test.csv` — CSV file used only for unsupported-format checks while tabular ingest is disabled

---

## Run Commands

```bash
# All tests
npx playwright test --project=chromium --headed

# P0 only
npx playwright test --project=chromium --grep "@p0"

# Specific spec
npx playwright test auth.spec.js --headed
```
