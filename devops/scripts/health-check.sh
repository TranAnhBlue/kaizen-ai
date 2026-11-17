#!/usr/bin/env bash
set -euo pipefail
API_URL="${API_URL:-http://localhost:3001/api/v1/health}"
AI_URL="${AI_URL:-http://localhost:8000/health}"
for url in "$API_URL" "$AI_URL"; do
  echo "Checking $url"
  curl --fail --silent --show-error --max-time 10 "$url" >/dev/null
done
echo 'Backend and AI service health endpoints responded.'
