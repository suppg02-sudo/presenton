# Contributing to Presenton

Thank you for your interest in contributing to Presenton! This document provides guidelines for contributing code, documentation, and feedback.

## Code of Conduct

Please be respectful and inclusive in all interactions.

## Getting Started

1. **Fork** the repository
2. **Clone** your fork: `git clone https://github.com/yourusername/presenton.git`
3. **Create** a feature branch: `git checkout -b feature/your-feature-name`
4. **Make** your changes
5. **Test** your changes
6. **Commit** with clear messages
7. **Push** to your fork
8. **Open** a pull request

## Development Setup

```bash
cd presenton
docker-compose up -d
# Wait for services to start
bash health_check.sh
```

## Code Standards

- Python: Follow PEP 8
- TypeScript/JavaScript: Use ESLint configuration
- Markdown: Use consistent formatting
- Commits: Use clear, descriptive messages

## Testing

All changes require tests:

```bash
# Run tests
pytest servers/fastapi/tests/ -v

# Check coverage
pytest --cov=servers/fastapi/services tests/
```

## Documentation

- Update docs for any user-facing changes
- Add docstrings to functions
- Include examples where helpful
- Update CHANGELOG.md

## Pull Request Process

1. **Update documentation** for any new features
2. **Add tests** for new functionality
3. **Verify tests pass** locally
4. **Update CHANGELOG.md**
5. **Request review** from maintainers
6. **Address feedback** from reviewers

## Reporting Issues

When reporting issues, include:
- **Description** of the problem
- **Steps** to reproduce
- **Expected** behavior
- **Actual** behavior
- **Environment** (OS, Docker version, etc.)
- **Logs** if applicable

## Areas for Contribution

### Code
- Bug fixes
- Performance improvements
- New features
- Test coverage improvements

### Documentation
- User guides
- API documentation
- Tutorials
- Troubleshooting guides

### Testing
- Additional test scenarios
- Load testing
- Edge case testing
- Integration testing

## License

By contributing, you agree that your contributions will be licensed under the project license.

## Questions?

- Check existing documentation
- Search GitHub issues
- Open a new issue if needed

---

Thank you for contributing to Presenton! 🎉
