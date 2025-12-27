# Security Policy

## Supported Versions

The following versions of `streamlit-lightweight-charts-v5` are currently supported with security updates:

| Version | Supported          | Notes                                    |
| ------- | ------------------ | ---------------------------------------- |
| 0.1.8   | :white_check_mark: | Current release - npm vulnerabilities: 9 |
| 0.1.7   | :white_check_mark: | Previous stable - critical fixes applied |
| 0.1.6   | :x:                | Deprecated - upgrade to 0.1.8            |
| < 0.1.6 | :x:                | No longer supported                      |

## Security Status (v0.1.8)

- **npm audit vulnerabilities**: 9 (reduced from 15 in v0.1.7)
  - 0 critical
  - 0 high
  - 9 moderate (dependency chain issues with limited exploit surface)
- **Direct dependencies**: All up-to-date and actively maintained
- **Python dependencies**: yfinance >=1.0 (rate limiting fixes)

## Reporting a Vulnerability

We take security vulnerabilities seriously. If you discover a security issue, please follow these steps:

### 1. Do Not Create a Public Issue

Please **do not** open a public GitHub issue for security vulnerabilities.

### 2. Report Privately

Send vulnerability reports via:
- **GitHub Security Advisories**: [Report a vulnerability](https://github.com/locupleto/streamlit-lightweight-charts-v5/security/advisories/new)
- **Email**: Include "[SECURITY]" in the subject line

### 3. Include in Your Report

- Description of the vulnerability
- Steps to reproduce the issue
- Potential impact assessment
- Affected versions
- Suggested fix (if available)

### 4. Response Timeline

- **Initial response**: Within 48 hours
- **Severity assessment**: Within 5 business days
- **Fix timeline**: Based on severity
  - Critical: Emergency patch within 7 days
  - High: Patch in next release (typically 2-4 weeks)
  - Medium/Low: Included in regular release cycle

### 5. Disclosure Policy

- We follow coordinated disclosure practices
- Security fixes are released before public disclosure
- Credit given to reporters (unless anonymity requested)

## Security Best Practices for Users

When using this component:

1. **Keep Dependencies Updated**
   ```bash
   pip install --upgrade streamlit-lightweight-charts-v5
   ```

2. **Validate Data Sources**
   - Sanitize user-provided chart data
   - Validate time series inputs
   - Be cautious with external data sources

3. **Use Latest Streamlit**
   - Keep Streamlit updated: `pip install --upgrade streamlit`
   - Monitor [Streamlit security advisories](https://github.com/streamlit/streamlit/security)

4. **Monitor npm Dependencies**
   - This component bundles JavaScript dependencies
   - Check release notes for frontend security updates

## Known Issues

### Moderate npm Vulnerabilities (9)

The remaining 9 moderate vulnerabilities are transitive dependencies in the React/build toolchain:
- Limited to development/build-time exposure
- No runtime exploit surface in production deployments
- Actively monitoring for patches from upstream maintainers

## Security Update History

| Version | Date       | Security Changes                                          |
| ------- | ---------- | --------------------------------------------------------- |
| 0.1.8   | 2025-12-27 | Reduced npm vulnerabilities from 15 to 9                  |
| 0.1.7   | 2025-06-20 | Removed js-yaml, timespan, uglify-js critical issues      |
| 0.1.6   | 2025-04-12 | General stability improvements                            |

## Acknowledgments

We appreciate the security research community's efforts in responsibly disclosing vulnerabilities. Contributors who report valid security issues will be credited in release notes (unless they prefer to remain anonymous).

---

**Last Updated**: 2025-12-27
**Version**: 0.1.8
