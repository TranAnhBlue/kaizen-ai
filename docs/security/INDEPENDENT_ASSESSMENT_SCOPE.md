# Scope for independent information-security assessment

**Status:** Draft scope for budgeting/procurement; no independent assessment has been conducted.

## Proposed scope
- External web app and API: authentication, authorization, multi-tenant isolation, session security, input validation, rate limiting, OWASP Top 10 / API risks.
- AI service: private network exposure, service-to-service auth, document ingestion, RAG prompt injection, data exfiltration, model endpoint security.
- Infrastructure: TLS, firewall, container configuration, image/dependency vulnerabilities, secret management, database and backup permissions.
- Operational controls: audit trail, log protection, monitoring, backup and restore, incident handling.

## Expected deliverables
- Agreed scope and methodology, test authorization and rules of engagement.
- Evidence-based report with risk classification, reproducible findings, affected assets, remediation recommendations.
- Remediation/retest record and final signed report from a suitably qualified independent organization.

## Budget planning
Estimate independently: scoping, vulnerability scanning, penetration testing, reporting, retest, and travel if applicable. Internal CI scans do **not** replace independent assessment.
