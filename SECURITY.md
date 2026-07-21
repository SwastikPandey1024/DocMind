# Security Policy

## Supported Versions

The following versions of DocMind are currently supported with security updates:

| Version | Supported          |
|---------|--------------------|
| 1.x     | ✅ Active          |
| < 1.0   | ❌ Not supported   |

We recommend all users run the latest stable version to benefit from security patches.

---

## Reporting a Vulnerability

We take the security of DocMind seriously. If you discover a security vulnerability, please follow our responsible disclosure process.

### How to Report

**Please do NOT report security vulnerabilities through public GitHub issues.**

Instead, report them via email to the project maintainers. If you're unsure who to contact, check the repository's commit history or GitHub profile for maintainer contact information.

When reporting, please include:

- **Type of issue** (e.g., XSS, SQL injection, authentication bypass)
- **Affected component** (backend, frontend, Docker configuration)
- **Steps to reproduce** — provide a proof of concept if possible
- **Impact assessment** — what an attacker could achieve
- **Suggested fix** (if available)

### What to Expect

1. **Acknowledgment** — We will acknowledge receipt within **5 business days**.
2. **Triage** — We will assess severity and impact within **10 business days**.
3. **Fix timeline** — We will develop and test a fix.
   - **Critical issues**: within 7 days
   - **High severity**: within 14 days
   - **Medium severity**: within 30 days
   - **Low severity**: next release cycle
4. **Release** — A patched version will be released.
5. **Disclosure** — We will publish a security advisory after the fix is released.

---

## Responsible Disclosure

We ask that you:

- Allow reasonable time for the fix before public disclosure
- Do not exploit the vulnerability beyond demonstrating the issue
- Do not access or modify user data without permission
- Act in good faith to improve the security of the project

We commit to:

- Respond promptly and professionally
- Keep you informed of progress
- Give credit for valid reports (if desired)
- Fix verified issues as quickly as possible

---

## Security Best Practices

### For Users

1. **Use strong, unique `JWT_SECRET`** — minimum 32 random characters
2. **Enable HTTPS** in production — use Let's Encrypt or a commercial CA
3. **Set secure environment variables** — never hardcode secrets
4. **Keep dependencies updated** — regularly update Python and npm packages
5. **Use Docker's security features** — read-only root filesystem, non-root users
6. **Restrict database access** — use strong passwords and network isolation

### For Deployers

```bash
# Generate a secure JWT secret
openssl rand -hex 32

# Run containers with limited privileges
docker compose run --read-only backend
```

### Production Hardening Checklist

- [ ] `JWT_SECRET` set to a strong, random value
- [ ] `APP_ENV=production` and `DEBUG=false`
- [ ] HTTPS/TLS enabled with valid certificates
- [ ] PostgreSQL password set via environment (not default)
- [ ] CORS configured to allow only your frontend domain
- [ ] File upload size limits configured
- [ ] Rate limiting enabled (reverse proxy level)
- [ ] Container resource limits set
- [ ] Regular database backups configured
- [ ] Log monitoring and alerting in place

---

## Security-Relevant Dependencies

| Dependency          | Purpose                     | Notes                           |
|---------------------|-----------------------------|---------------------------------|
| python-jose         | JWT token handling          | Keep updated for CVEs           |
| argon2              | Password hashing            | Strongest available algorithm   |
| psycopg2            | PostgreSQL driver           | SQL injection via ORM only      |
| opencv-python       | Image processing            | Use headless variant in Docker  |
| fastapi             | API framework               | Built-in validation & security  |

---

## Known Security Considerations

- **File uploads**: Validated by type, size, and checksum before processing
- **SQL injection**: Prevented by SQLAlchemy ORM usage (no raw queries)
- **XSS**: Mitigated by React's automatic HTML escaping
- **CSRF**: API uses JWT tokens (stateless authentication)
- **Authentication**: JWT with short-lived access tokens (15 min) and refresh tokens (7 days)

---

## Vulnerability Disclosure History

| Date       | Severity | Component   | Issue                         | Fixed In     |
|------------|----------|-------------|-------------------------------|--------------|
| —          | —        | —           | No reported vulnerabilities   | —            |

---

We appreciate the community's help in keeping DocMind secure. Thank you for acting responsibly.

