import assert from 'node:assert/strict';

console.error = () => {};

globalThis.localStorage = {
    getItem: (key) => (key === 'accessToken' ? 'test-token' : null),
};

globalThis.FormData = class {
    constructor() {
        this.fields = [];
    }
    append(key, value) {
        this.fields.push([key, value]);
    }
};

const calls = [];

function jsonResponse(payload) {
    return {
        ok: true,
        json: async () => payload,
    };
}

function streamResponse(chunks) {
    const encoder = new TextEncoder();
    return {
        ok: true,
        body: new ReadableStream({
            start(controller) {
                chunks.forEach((chunk) => controller.enqueue(encoder.encode(chunk)));
                controller.close();
            },
        }),
        json: async () => ({}),
    };
}

globalThis.fetch = async (url, options = {}) => {
    calls.push({ url, method: options.method || 'GET', body: options.body });

    if (url === `${BASE_URL}/documents` && options.method === 'POST') {
        return jsonResponse({
            document_id: 'doc-1',
            job_id: 'job-1',
            status: 'queued',
            pipeline_version: '1.0.0',
            object_key: 'doc-1/sample.pdf',
        });
    }

    if (url === `${BASE_URL}/documents` && (!options.method || options.method === 'GET')) {
        return jsonResponse([
            { document_id: 'doc-1', filename: 'sample.pdf' },
            { document_id: 'doc-2', filename: 'notes.pdf' },
        ]);
    }

    if (url === `${BASE_URL}/documents?notebook_id=42` && (!options.method || options.method === 'GET')) {
        return jsonResponse([
            { document_id: 'doc-1', notebook_id: 42, filename: 'sample.pdf' },
        ]);
    }

    if (url === `${BASE_URL}/jobs/job-1` && (!options.method || options.method === 'GET')) {
        return jsonResponse({
            job_id: 'job-1',
            status: 'succeeded',
            stage: 'persisting_metadata',
            progress_pct: 100,
        });
    }

    if (url === `${BASE_URL}/chat/stream` && options.method === 'POST') {
        const payload = JSON.parse(options.body);
        if (payload.message === 'stream error') {
            return streamResponse(['data: {"type":"error","token":"","done":true,"error":"boom","citations":[]}\n\n']);
        }
        return streamResponse([
            'data: {"type":"token","token":"Hello","done":false}\n\n',
            'data: {"type":"final","token":"","done":true,"answer":"Hello [C1]","citations":[{"citation_id":"C1","source":"sample.pdf","page":3}],"conversation_id":"conv-1","message_id":"msg-1","rewritten_query":"test"}\n\n',
        ]);
    }

    return {
        ok: false,
        status: 404,
        json: async () => ({ detail: `Unexpected URL: ${url}` }),
    };
};

const { BASE_URL } = await import('../src/api/client.js');
const { uploadDocument, listSources, getJob, chatStream } = await import('../src/api/rag.js');

assert.equal(BASE_URL, '/api');

const uploadResult = await uploadDocument({ name: 'sample.pdf' }, { notebookId: 42 });
assert.equal(calls[0].url, `${BASE_URL}/documents`);
assert.equal(calls[0].method, 'POST');
assert.deepEqual(calls[0].body.fields.map(([key, value]) => [key, String(value?.name || value)]), [
    ['file', 'sample.pdf'],
    ['notebook_id', '42'],
]);
assert.equal(uploadResult.job_id, 'job-1');

const sourcesResult = await listSources();
assert.equal(calls[1].url, `${BASE_URL}/documents`);
assert.equal(calls[1].method, 'GET');
assert.deepEqual(sourcesResult.sources, ['sample.pdf', 'notes.pdf']);
assert.equal(sourcesResult.count, 2);
assert.equal(sourcesResult.has_sources, true);
assert.equal(sourcesResult.documents.length, 2);

const notebookSourcesResult = await listSources({ notebookId: 42 });
assert.equal(calls[2].url, `${BASE_URL}/documents?notebook_id=42`);
assert.equal(calls[2].method, 'GET');
assert.deepEqual(notebookSourcesResult.sources, ['sample.pdf']);
assert.equal(notebookSourcesResult.documents[0].notebook_id, 42);

const jobResult = await getJob('job-1');
assert.equal(calls[3].url, `${BASE_URL}/jobs/job-1`);
assert.equal(calls[3].method, 'GET');
assert.equal(jobResult.status, 'succeeded');

const streamFinal = await new Promise((resolve, reject) => {
    chatStream('test', {
        onToken(token) {
            assert.equal(token, 'Hello');
        },
        onDone(payload) {
            resolve(payload);
        },
        onError(error) {
            reject(error);
        },
    });
});
assert.equal(streamFinal.answer, 'Hello [C1]');
assert.equal(streamFinal.citations[0].citation_id, 'C1');
assert.equal(streamFinal.citations[0].source, 'sample.pdf');
assert.equal(streamFinal.citations[0].page, 3);

const streamError = await new Promise((resolve) => {
    chatStream('stream error', {
        onDone() {
            resolve(null);
        },
        onError(error) {
            resolve(error);
        },
    });
});
assert.equal(streamError.message, 'boom');
