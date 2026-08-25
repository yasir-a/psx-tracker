# Security Policy

## 1. Supported Versions

We provide security updates and patches for the following versions:

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |
| < 0.1.0 | :x:                |

---

## 2. Reporting a Vulnerability

We take the security of the PSX Portfolio Tracker seriously. If you discover a security vulnerability, please report it responsibly:

* **Email:** Please report security issues directly to the maintainer at `security@psxportfoliotracker.org` (or directly to repository maintainers via private GitHub security advisory).
* **Information to Include:**
  * Description of the vulnerability
  * Steps to reproduce or proof-of-concept
  * Affected endpoints, components, or files
  * Potential impact assessment
* **Response Timeline:** We aim to acknowledge receipt within 48 hours and provide a remediation timeline or patch within 7 business days.
* **Public Disclosure:** Please do NOT file public GitHub issues for sensitive security vulnerabilities until a fix has been verified and released.

---

## 3. Security Principles for Development

* **No Plaintext Secrets:** Passwords, API keys, database credentials, and session secrets must never be committed to the repository.
* **Authentication & Passwords:** Passwords must be hashed using strong, modern algorithms (Argon2 / Bcrypt).
* **Input Validation & Injection Prevention:** All SQL queries must be parameterized. User inputs must be strictly validated before processing.
* **Authoritative Financial Data:** Financial states must be computed from verified transaction records in PostgreSQL, never trusting client-provided totals.
* **Rate Limiting:** Authentication and resource-intensive endpoints must be rate-limited to mitigate brute-force and denial-of-service attempts.

