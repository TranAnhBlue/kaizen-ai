#!/usr/bin/env python3
"""Unauthenticated smoke checks only; optional target URLs via environment."""
import json, os, sys, urllib.error, urllib.request
urls={
 'backend':os.getenv('BACKEND_HEALTH_URL','http://localhost:3001/api/v1/health'),
 'ai':os.getenv('AI_HEALTH_URL','http://localhost:8000/health'),
}
failed=[]
for name,url in urls.items():
 try:
  with urllib.request.urlopen(url,timeout=5) as response:
   payload=json.load(response)
   if response.status!=200 or payload.get('status')!='ok': raise ValueError('Unexpected health response')
   print('PASS',name,url)
 except (urllib.error.URLError,ValueError,TimeoutError) as exc:
  print('FAIL',name,url,str(exc));failed.append(name)
sys.exit(bool(failed))
