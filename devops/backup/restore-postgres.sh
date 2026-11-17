#!/usr/bin/env bash
set -euo pipefail
: "${RESTORE_DATABASE_URL:?Explicit RESTORE_DATABASE_URL required}"
: "${1:?Usage: restore-postgres.sh backup.dump}"
if [ "${CONFIRM_RESTORE:-}" != 'YES' ]; then echo 'Set CONFIRM_RESTORE=YES after verifying target database' >&2; exit 1; fi
pg_restore --dbname="$RESTORE_DATABASE_URL" --no-owner --no-acl --exit-on-error "$1"
echo 'Restore finished; run application integrity checks.'
