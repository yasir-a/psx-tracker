# Contributing to PSX Portfolio Tracker

Thank you for your interest in contributing to the **PSX Portfolio Tracker**! This project is an open-source, production-grade application designed for the Pakistan Stock Exchange community.

---

## 1. Code of Conduct

All contributors and maintainers are expected to adhere to our [Code of Conduct](CODE_OF_CONDUCT.md). Please report unacceptable behavior following the guidelines in that document.

---

## 2. Git Workflow & Branching Strategy

* **Protected Main:** The `main` branch is protected. Direct commits to `main` are prohibited. All changes enter `main` via reviewed and CI-validated Pull Requests.
* **Branch Naming:**
  * `feature/<feature-name>`: New capabilities or additions
  * `fix/<bug-description>`: Bug fixes
  * `docs/<topic>`: Documentation updates
  * `test/<suite-name>`: Test improvements or additions
  * `refactor/<target>`: Structural or performance refactoring without behavioral change
  * `chore/<tooling>`: Maintenance, CI, dependencies

---

## 3. Commit Message Guidelines

We enforce the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```text
<type>(<optional scope>): <description>

[optional body]

[optional footer(s)]
```

### Supported Types
* `feat`: A new feature
* `fix`: A bug fix
* `docs`: Documentation only changes
* `test`: Adding or correcting tests
* `refactor`: Code change that neither fixes a bug nor adds a feature
* `perf`: A code change that improves performance
* `chore`: Changes to build process, auxiliary tools, or libraries
* `security`: Security patches and dependency vulnerability mitigations

---

## 4. Pull Request Process

1. Fork the repository and create your branch from `main`.
2. Follow domain decoupling and architecture principles outlined in `AGENTS.md`.
3. Add deterministic unit/integration tests for all new code. Financial calculation changes require exhaustive test coverage.
4. Ensure all linters, type checkers, and tests pass locally.
5. Update `FEATURES.md` and `CHANGELOG.md` where appropriate.
6. Open a Pull Request using the standard [Pull Request Template](.github/PULL_REQUEST_TEMPLATE.md).
7. Address any code review feedback promptly.

---

## 5. Development Standards

* **Backend (Python):**
  * Type hints are mandatory.
  * Keep domain logic framework-independent in `backend/src/domain/`.
  * Use `Decimal` for all currency and financial quantity math. Never use `float`.
* **Frontend (React/TypeScript):**
  * Strict TypeScript mode enabled.
  * Accessibility-first (semantic HTML, proper ARIA attributes, keyboard navigation).
  * Responsive layout matching modern design patterns.

