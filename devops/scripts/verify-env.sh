#!/usr/bin/env bash
set -euo pipefail
: "${DATABASE_URL:?DATABASE_URL is required}"
: "${JWT_SECRET:?JWT_SECRET is required}"
: "${AI_SERVICE_TOKEN:?AI_SERVICE_TOKEN is required}"
if [ "${#JWT_SECRET}" -lt 32 ] || [ "${#AI_SERVICE_TOKEN}" -lt 32 ]; then
 echo 'JWT_SECRET and AI_SERVICE_TOKEN must each be at least 32 characters' >&2; exit 1
fi
case "$JWT_SECRET:$AI_SERVICE_TOKEN" in *replace-with*|*change-this*) echo 'Replace placeholder secrets' >&2; exit 1;; esac
echo 'Required environment values are present (secrets not printed).'
