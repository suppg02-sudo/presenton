# Security Policy

## Security Best Practices

### API Security
- **No hardcoded secrets** - All API keys in environment variables
- **CORS configured** - Restrict API access to trusted origins
- **Rate limiting** - Implemented to prevent abuse
- **Input validation** - All API inputs validated
- **Error handling** - Sensitive errors not exposed to users

### Authentication
- OpenRouter API key stored in environment variable
- No API keys in logs or responses
- API endpoints require proper authentication (if implemented)

### Data Security
- **Database**: SQLite with file permissions
- **Metrics**: Collected anonymously, no PII
- **Logs**: Sanitized before storage
- **Backups**: Encrypted and stored securely

### Deployment Security
- **Containers**: Run as non-root user
- **Volumes**: Mounted with proper permissions
- **Networks**: Isolated from public internet
- **Ports**: Only necessary ports exposed
- **SSL/TLS**: Enabled for production

### Code Security
- **Dependencies**: Regularly updated
- **Code review**: All changes reviewed
- **Testing**: Security-focused test cases
- **Linting**: Code quality checks before deployment

## Vulnerability Reporting

**Please report security vulnerabilities responsibly:**

1. **Do NOT** open a public issue
2. **Email** security@presenton.dev with:
   - Description of vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)
3. **Wait** for response before disclosing

## Security Checklist

- [ ] All API keys in environment variables
- [ ] CORS origins restricted
- [ ] SSL/TLS enabled in production
- [ ] Database file permissions (0600)
- [ ] Log files contain no secrets
- [ ] Backups encrypted
- [ ] Monitoring/alerting enabled
- [ ] Regular security updates

## Third-Party Services

### OpenRouter
- Free tier models only (no premium billing)
- API key required but safe in env vars
- No user data sent to OpenRouter except for inference

### Pexels (Optional)
- Only used if image generation enabled
- API key managed securely
- No user data sent

## Container Security

- Containers run as non-root (UID 1000+)
- Read-only root filesystem where possible
- Network isolation between services
- Resource limits enforced
- Health checks monitor availability

## Compliance

- GDPR: Metrics collected anonymously
- CCPA: No user data stored
- PCI-DSS: Not applicable (no payment processing)

## Support

For security questions or concerns:
- Email: security@presenton.dev
- Docs: See SECURITY.md in repository

---

Last Updated: February 18, 2026
