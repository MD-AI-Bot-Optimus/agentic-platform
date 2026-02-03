# Contributing Guide

## Code of Conduct

Be respectful, inclusive, and professional in all interactions.

## Development Setup

```bash
# Clone repository
git clone https://github.com/your-org/agentic-platform.git
cd agentic-platform

# Setup Python environment
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Setup Node environment
cd ui
npm install
cd ..

# Verify setup
python -m pytest tests/
```

## Architecture Principles

1. **Adapter Pattern**: All integrations use adapter pattern for loose coupling
2. **Test-Driven Development**: Write tests before implementation
3. **Clean Code**: Follow PEP 8, use type hints
4. **Documentation**: Update docs for all changes
5. **ADRs**: Create Architecture Decision Records for significant decisions

## Commit Convention

```
<type>(<scope>): <subject>

<body>

<footer>
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

Example:
```
feat(ocr): add batch image processing

- Support processing multiple images in one request
- Add progress reporting
- Improve performance with parallel processing

Closes #123
```

## Testing Requirements

- **Unit Tests**: Test individual components in isolation
- **Integration Tests**: Test component interactions
- **End-to-End Tests**: Test complete workflows
- **Minimum Coverage**: 80% code coverage

Run tests:
```bash
pytest tests/
pytest tests/ --cov=src/
```

## Code Quality

### Python
```bash
# Format
black src/ tests/

# Lint
ruff check src/ tests/

# Type check
mypy src/
```

### JavaScript/React
```bash
cd ui
npm run lint
npm run test
```

## Pull Request Process

1. Create feature branch: `git checkout -b feat/feature-name`
2. Make changes following code style guidelines
3. Write/update tests
4. Update documentation
5. Push and create pull request with description
6. Address review comments
7. Squash commits: `git rebase -i`
8. Merge to main

## Adding New Features

### New Tool/Adapter

1. Create adapter class in `src/agentic_platform/adapters/`
2. Implement tool interface
3. Add integration tests in `tests/integration/`
4. Document in `docs/adapters.md`
5. Create ADR if architectural impact

### New Workflow Node Type

1. Extend node handler in `src/agentic_platform/workflow/engine.py`
2. Add validation schema
3. Implement in workflow parser
4. Test with YAML workflows
5. Document with examples

### New API Endpoint

1. Add route in `src/agentic_platform/api.py`
2. Document with OpenAPI annotations
3. Add validation and error handling
4. Create integration test
5. Update API docs

## Documentation

All significant changes must include documentation:

- **Code Comments**: Explain "why", not "what"
- **Docstrings**: Google-style docstrings for functions
- **README**: Update if user-facing changes
- **API Docs**: Ensure endpoints are properly documented
- **ADRs**: Create for architectural decisions

## Performance Considerations

1. **Latency**: Track API response times
2. **Memory**: Monitor memory usage in workflows
3. **Concurrency**: Test with multiple concurrent requests
4. **Scaling**: Ensure stateless design for horizontal scaling

## Security Checklist

- [ ] No credentials in code or logs
- [ ] Input validation on all endpoints
- [ ] CORS configured appropriately
- [ ] Rate limiting implemented for public endpoints
- [ ] Error messages don't expose internals
- [ ] Dependencies checked for vulnerabilities

## Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for:
- Local Docker builds
- Google Cloud Run deployment
- CI/CD integration
- Monitoring and logging

## Questions?

- Check existing [ADRs](docs/decisions/)
- Review [API documentation](docs/api.md)
- Check [Architecture docs](docs/architecture.md)
- Open an issue for discussion
