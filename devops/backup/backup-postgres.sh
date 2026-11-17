#!/usr/bin/env bash
set -euo pipefail
: "${DATABASE_URL:?DATABASE_URL required}"
OUT_DIR="${BACKUP_DIR:-./backups}"
mkdir -p "$OUT_DIR"
chmod 700 "$OUT_DIR"
FILE="$OUT_DIR/kaizen-$(date -u +%Y%m%dT%H%M%SZ).dump"
umask 077
pg_dump --format=custom --no-owner --no-acl --file="$FILE" "$DATABASE_URL"
test -s "$FILE"
echo "Backup saved: $FILE"
