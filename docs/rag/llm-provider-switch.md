# LLM Provider Switch

This repo now resolves the runtime chat provider through `rag_core/common/llm.py`.

## What changed

- `rag_core/common/llm.py` is the shared provider resolver and client factory.
- `LLM_PROVIDER=auto` now selects the provider from `LLM_MODEL`.
- Models that start with `gemini` use Gemini.
- All other model names use the OpenCode OpenAI-compatible API.
- `rag_core/step4_generator.py`, `backend/app/services/chat_runtime.py`, and `backend/app/services/rag_service.py` all call the shared factory, so the behavior is consistent across the pipeline and chat API.

## What `auto` means

- `LLM_PROVIDER=auto` means "infer the provider from the model name".
- `gemini-3.1-flash-lite-preview` resolves to Gemini.
- `deepseek-v4-flash` resolves to OpenCode.
- If `LLM_PROVIDER` is set explicitly to `gemini` or `opencode`, that value wins over model-name inference.
- `LLM_MODE=auto` is separate from `LLM_PROVIDER=auto`; backend chat will try the inferred cloud provider first and fall back to local Ollama only when the cloud provider is unavailable.
- For cloud model switching, keep `LLM_MODE=gemini` if you do not want local fallback, or use `LLM_MODE=auto` if local fallback should remain available. Provider choice still comes from `LLM_PROVIDER` and `LLM_MODEL`.

## Switching providers

### Gemini

```env
LLM_PROVIDER=auto
LLM_MODEL=gemini-3.1-flash-lite-preview
GEMINI_API_KEY=your-gemini-api-key-here
```

You can also pin it explicitly:

```env
LLM_PROVIDER=gemini
LLM_MODEL=gemini-3.1-flash-lite-preview
GEMINI_API_KEY=your-gemini-api-key-here
```

### OpenCode

```env
LLM_PROVIDER=auto
LLM_MODEL=deepseek-v4-flash
OPENCODE_API_KEY=your-opencode-go-api-key-here
OPENCODE_API_BASE=https://opencode.ai/zen/go/v1
```

You can also pin it explicitly:

```env
LLM_PROVIDER=opencode
LLM_MODEL=deepseek-v4-flash
OPENCODE_API_KEY=your-opencode-go-api-key-here
OPENCODE_API_BASE=https://opencode.ai/zen/go/v1
```

## Required env vars

- `LLM_MODEL`: required for the runtime model name.
- `LLM_PROVIDER`: `auto`, `gemini`, or `opencode`.
- `GEMINI_API_KEY`: required when the resolved provider is Gemini.
- `OPENCODE_API_KEY`: required when the resolved provider is OpenCode.
- `OPENCODE_API_BASE`: OpenCode endpoint, defaults to `https://opencode.ai/zen/go/v1`.
- `LLM_MODE`: backend runtime behavior (`auto`, `gemini`, `opencode`, or `local`). `auto` enables local fallback; `local` bypasses cloud providers.
- `LOCAL_LLM_BASE_URL` and `LOCAL_LLM_MODEL`: only needed when you use `LLM_MODE=auto` fallback or `LLM_MODE=local`.

Note: the OpenCode runtime path uses `OPENCODE_API_KEY` and `OPENCODE_API_BASE`; it does not use `OPENAI_API_KEY` for this switch.

## Restart and validation

- Restart the backend API and ingest worker after changing `.env` values. These settings are read at process start.
- If you are running Docker Compose, restart the API service and the worker service together.
- Validate the resolver with `python -m unittest rag_core.tests.test_llm -v`.
- Validate the backend fallback path with `python -m unittest backend.tests.test_chat_runtime_modes -v`.
- Then exercise `POST /api/chat` and `POST /api/chat/stream`. If the cloud provider is unavailable in `LLM_MODE=auto`, fallback logs should name the inferred provider.
