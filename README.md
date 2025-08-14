# CDC SSO validator service

What it does
- Accepts an incoming sso_key
- Performs a GET to the SSO server with ?ssoKey=<...>
- Attempts to base64-decode the returned payload
- If the decoded value is JSON, it returns parsed JSON; otherwise returns text

Run locally
  pip install fastapi uvicorn httpx
  uvicorn app:app --host 0.0.0.0 --port 8000 --reload

Example
```
curl -X POST http://localhost:8000/validate \
     -H 'Content-Type: application/json' \
     -d '{
            "sso_key": "abc123..."
        }'
```