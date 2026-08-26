# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Added
- **Phase 1: Backend Foundation (Flask)**
  - Application factory pattern in `backend/src/app.py`.
  - Type-safe, environment-aware configuration via `pydantic-settings` in `backend/src/config.py`.
  - Structured error hierarchy (`AppError`, `ValidationError`, `NotFoundError`, `UnauthorizedError`, `ForbiddenError`) and JSON error handlers in `backend/src/api/errors.py`.
  - Request ID injection and latency logging middleware in `backend/src/api/middleware.py`.
  - Health (`/api/v1/health`) and Readiness (`/api/v1/ready`) endpoints in `backend/src/api/v1/health.py`.
  - Pytest unit test suite covering configuration, error handlers, and health endpoints.
- **Phase 0: Governance & Architecture Baseline**
  - Project governance documents: `README.md`, `AGENTS.md`, `FEATURES.md`, `CONTRIBUTING.md`, `SECURITY.md`, `CODE_OF_CONDUCT.md`, `LICENSE`.
  - Issue templates for bug reports and feature requests.
  - Pull request template.
  - Initial architecture blueprints defining modular monolith, FIFO lot accounting, Flask backend layout, PostgreSQL persistence, and Redis caching boundary.

