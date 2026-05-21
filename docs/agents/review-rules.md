# Review Rules

## Code Review Checklist

### Before Submitting

- [ ] Tests pass: `python -m unittest test_* -v`
- [ ] Pipeline smoke test: `python rag_core/main_test.py`
- [ ] No hardcoded values (use config.py)
- [ ] Logging added for important operations
- [ ] No secrets/keys in code

### Architecture

- [ ] Changes follow single-responsibility (step1-4 structure)
- [ ] Shared logic in `rag_core/common/`
- [ ] Metadata keys preserved: source, page, doc_id

### Python Style

- [ ] snake_case for functions/variables
- [ ] PascalCase for classes
- [ ] UPPER_SNAKE_CASE for constants
- [ ] 4-space indentation
- [ ] No trailing whitespace

### JavaScript Style

- [ ] camelCase for functions/variables
- [ ] kebab-case for CSS classes
- [ ] Single quotes for strings
- [ ] Semicolons present

### Security

- [ ] API keys in .env only
- [ ] Passwords hashed (Argon2)
- [ ] JWT validation works
- [ ] Input validation on endpoints

## Review Process

1. **Self-review**: Check checklist above
2. **Testing**: Run all tests locally
3. **Documentation**: Update docs/ if needed
4. **Commit message**: Clear, concise, explains "why"

## Common Issues to Catch

| Issue | Prevention |
|-------|------------|
| Hardcoded paths | Use Config class |
| Missing error handling | Add try/catch + logging |
| No tests for new feature | Write tests first (TDD) |
| Breaking existing tests | Run full test suite before commit |