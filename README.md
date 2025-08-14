# CDC SSO validator service

What it does
- Accepts an incoming sso_key
- Performs a GET to the SSO server with ?ssoKey=<...>
- Attempts to base64-decode the returned payload
- If the decoded value is JSON, it returns parsed JSON; otherwise returns text

Run locally
```
make build
make run
make stop
```

Example
```
curl -X POST http://localhost:8000/validate \
     -H 'Content-Type: application/json' \
     -d '{
            "sso_key": "abc123..."
        }'
```