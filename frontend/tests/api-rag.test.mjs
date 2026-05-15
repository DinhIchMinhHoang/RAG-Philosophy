import assert from 'node:assert/strict';

globalThis.localStorage = {
    getItem: (key) => (key === 'accessToken' ? 'test-token' : null),
};

globalThis.FormData = class {
    append() {}
};

const calls = [];

function jsonResponse(payload) {
    return {
        ok: true,
        json: async () => payload,
    };
}

globalThis.fetch = async (url, options = {}) => {
    calls.push({ url, method: options.method || 'GET' });

    if (url === '/api/documents' && options.method === 'POST') {
        return jsonResponse({
            document_id: 'doc-1',
            job_id: 'job-1',
            status: 'queued',
            pipeline_version: '1.0.0',
            object_key: 'doc-1/sample.pdf',
        });
    }

    if (url === '/api/documents' && (!options.method || options.method === 'GET')) {
        return jsonResponse([
            { document_id: 'doc-1', filename: 'sample.pdf' },
            { document_id: 'doc-2', filename: 'notes.pdf' },
        ]);
    }

    if (url === '/api/jobs/job-1' && (!options.method || options.method === 'GET')) {
        return jsonResponse({
            job_id: 'job-1',
            status: 'succeeded',
            stage: 'persisting_metadata',
            progress_pct: 100,
        });
    }

    return {
        ok: false,
        status: 404,
        json: async () => ({ detail: `Unexpected URL: ${url}` }),
    };
};

const { uploadDocument, listSources, getJob } = await import('../src/api/rag.js');

const uploadResult = await uploadDocument({ name: 'sample.pdf' });
assert.equal(calls[0].url, '/api/documents');
assert.equal(calls[0].method, 'POST');
assert.equal(uploadResult.job_id, 'job-1');

const sourcesResult = await listSources();
assert.equal(calls[1].url, '/api/documents');
assert.equal(calls[1].method, 'GET');
assert.deepEqual(sourcesResult.sources, ['sample.pdf', 'notes.pdf']);
assert.equal(sourcesResult.count, 2);
assert.equal(sourcesResult.has_sources, true);
assert.equal(sourcesResult.documents.length, 2);

const jobResult = await getJob('job-1');
assert.equal(calls[2].url, '/api/jobs/job-1');
assert.equal(calls[2].method, 'GET');
assert.equal(jobResult.status, 'succeeded');
