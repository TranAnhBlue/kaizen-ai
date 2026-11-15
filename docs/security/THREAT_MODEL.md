# Initial threat model
Assets: enterprise KPI, Kaizen initiatives, documents, AI prompts, credentials.
Trust boundaries: browser/API; API/AI; API/database; AI/vector search.
Risks: IDOR, tenant crossover, prompt injection, data exfiltration, malicious documents, insecure model outputs, secret leakage, supply chain vulnerabilities.
Mitigations to implement before production: tenant-scoped auth, service identity, deny-by-default document ACL, encrypted transport, least privilege DB users, scanning, logging redaction, test evidence.
