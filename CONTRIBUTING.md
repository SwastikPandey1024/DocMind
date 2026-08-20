# Contributing to DocuChat

Thank you for your interest in contributing to **DocuChat** — the AI-powered OCR + RAG Document Chat System. We welcome contributions from everyone, whether it's a bug fix, feature enhancement, documentation improvement, or any other form of contribution.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Development Setup](#development-setup)
- [Development Workflow](#development-workflow)
  - [Branch Naming Convention](#branch-naming-convention)
  - [Commit Message Convention](#commit-message-convention)
  - [Pull Request Process](#pull-request-process)
- [Coding Standards](#coding-standards)
  - [Python (Backend)](#python-backend)
  - [TypeScript/React (Frontend)](#typescriptreact-frontend)
  - [Documentation](#documentation)
- [Testing Guidelines](#testing-guidelines)
- [Issue Reporting](#issue-reporting)
- [Feature Requests](#feature-requests)

---

## Code of Conduct

This project is governed by the [Contributor Covenant](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code. Please report unacceptable behavior to the project maintainers.

---

## Getting Started

### Prerequisites

Make sure you have the following installed:

- **Python** 3.12+
- **Node.js** 20+
- **npm** (comes with Node.js)
- **Docker** & **Docker Compose** (recommended for local database)
- **Git**

### Development Setup

1. **Fork the repository** and clone your fork:

   ```bash
   git clone https://github.com/your-username/DocuChat.git
   cd DocuChat
   ```

2. **Add the upstream remote:**

   ```bash
   git remote add upstream https://github.com/SwastikPandey1024/DocuChat.git
   ```

3. **Set up the backend:**

   ```bash
   cd backend
   python -m venv venv

   # On Linux/macOS:
   source venv/bin/activate

   # On Windows:
   venv\Scripts\activate

   pip install -r requirements.txt
   ```

4. **Set up the frontend:**

   ```bash
   cd frontend
   npm install
   ```

5. **Start the database** (using Docker):

   ```bash
   docker compose up -d postgres
   ```

6. **Run database migrations:**

   ```bash
   cd backend
   alembic upgrade head
   ```

7. **Start development servers:**

   ```bash
   # Terminal 1: Backend
   cd backend
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

   # Terminal 2: Frontend
   cd frontend
   npm run dev
   ```

8. **Verify setup:** Open http://localhost:3000 and http://localhost:8000/docs

---

## Development Workflow

### Branch Naming Convention

Use descriptive branch names that follow this format:

| Prefix      | Example                          | Purpose                          |
|-------------|----------------------------------|----------------------------------|
| `feature/`  | `feature/document-summarization` | New features                     |
| `bugfix/`   | `bugfix/ocr-timeout-error`       | Bug fixes                        |
| `hotfix/`   | `hotfix/security-vulnerability`  | Urgent production fixes          |
| `docs/`     | `docs/api-authentication`        | Documentation changes            |
| `refactor/` | `refactor/service-layer`         | Code refactoring                 |
| `test/`     | `test/embedding-service`         | Adding or updating tests         |
| `chore/`    | `chore/update-dependencies`      | Maintenance tasks                |

### Commit Message Convention

We follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

**Types:**

- `feat` — A new feature
- `fix` — A bug fix
- `docs` — Documentation changes
- `style` — Code style changes (formatting, etc.)
- `refactor` — Code refactoring
- `perf` — Performance improvements
- `test` — Adding or updating tests
- `chore` — Maintenance tasks
- `ci` — CI/CD changes
- `security` — Security fixes

**Examples:**

```
feat(ocr): add multi-language OCR support for French and German
fix(chat): handle empty document context gracefully
docs(readme): update installation instructions for Windows
test(embedding): add unit tests for batch encoding
```

### Pull Request Process

1. **Create a branch** from `main` using the naming convention above.
2. **Make your changes** following the coding standards.
3. **Test your changes** thoroughly.
4. **Update documentation** if applicable.
5. **Push your branch** and open a Pull Request.
6. **Fill out the PR template** completely.
7. **Request a review** from maintainers.
8. **Address review feedback** promptly.

**Pull Request Checklist:**

- [ ] Code follows project coding standards
- [ ] Self-review completed
- [ ] Documentation updated (if needed)
- [ ] No new warnings or errors
- [ ] Tests pass (if tests exist)
- [ ] Branch is up to date with `main`
- [ ] Commit messages follow conventions

---

## Coding Standards

### Python (Backend)

- Follow [PEP 8](https://peps.python.org/pep-0008/) style guide
- Use **type hints** for all function signatures
- Run **Black** for code formatting: `black .`
- Run **Ruff** for linting: `ruff check .`
- Run **mypy** for type checking: `mypy app/`
- Use **docstrings** for all public modules, classes, and functions
- Keep functions focused and single-purpose
- Maximum line length: 88 characters (Black default)

**Example:**

```python
from typing import Optional


def process_document(document_id: str, language: Optional[str] = None) -> dict:
    """Process a document through the OCR pipeline.

    Args:
        document_id: The UUID of the document to process.
        language: Optional language override for OCR.

    Returns:
        A dictionary containing the processing result.

    Raises:
        DocumentNotFoundError: If the document does not exist.
        ProcessingError: If OCR processing fails.
    """
    ...
```

### TypeScript/React (Frontend)

- Use **TypeScript** with strict mode
- Follow the existing component patterns
- Use functional components with hooks
- Run **ESLint**: `npm run lint`
- Write **self-documenting code** with clear variable names
- Use **Radix UI** primitives for accessible components
- Style with **TailwindCSS** utility classes

### Documentation

- Keep documentation in sync with code changes
- Use clear, concise language
- Include code examples where helpful
- Update README if adding new features
- Document API changes in OpenAPI/Swagger

---

## Testing Guidelines

We encourage adding tests for all contributions:

- **Unit tests** for individual service functions
- **Integration tests** for API endpoints
- **Coverage** for critical paths (OCR, RAG, auth)

Run tests locally:

```bash
# Backend tests
cd backend
pytest tests/ -v

# With coverage
pytest --cov=app tests/
```

---

## Issue Reporting

When reporting a bug, please include:

- A clear description of the issue
- Steps to reproduce
- Expected vs actual behavior
- Environment details (OS, Python version, Docker version)
- Relevant logs or screenshots

Use the [Bug Report template](.github/ISSUE_TEMPLATE/bug_report.md).

---

## Feature Requests

We welcome feature suggestions! When proposing a new feature:

- Describe the problem it solves
- Explain the proposed solution
- Consider alternative approaches
- Include any relevant use cases

Use the [Feature Request template](.github/ISSUE_TEMPLATE/feature_request.md).

---

## Questions?

If you have questions, feel free to:

- Open a [Discussion](https://github.com/SwastikPandey1024/DocuChat/discussions)
- Check the [Documentation](ARCHITECTURE.md)

---

**Thank you for contributing to DocuChat! 🚀**

