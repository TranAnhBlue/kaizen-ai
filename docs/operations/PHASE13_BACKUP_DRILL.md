# Phase 13 — Backup / restore drill record

Do not restore over production. Use a separate disposable PostgreSQL instance and an approved backup copy. Before restoring, verify the destination database name, access privileges, retention policy, and backup checksum. Follow `devops/backup/README.md` and inspect scripts before execution.

Record: UTC time, source database alias, backup filename and SHA-256, encrypted storage location, destination test database, operator, backup duration, restore duration, verification SQL row counts, application smoke-test results, RPO/RTO observed, issues and sign-off.

**Completion status:** Template only. A real restore drill is not claimed until completed with recorded evidence.
