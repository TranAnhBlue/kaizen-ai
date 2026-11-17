#!/usr/bin/env bash
set -euo pipefail
FILE="${1:?Usage: verify-backup.sh backup.dump}"
test -s "$FILE"
pg_restore --list "$FILE" >/dev/null
echo 'Archive is readable; a separate restore test is still required.'
