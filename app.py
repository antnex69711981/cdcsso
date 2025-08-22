from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import httpx
import base64
import json
import logging
import datetime
from ldap3 import SIMPLE, Server, Connection, ALL

app = FastAPI()

logging.basicConfig(level=logging.INFO)
BASE_SSO_URL = "http://192.168.171.27:8080/api/values/CheckKey?SSOkey="

class ValidateRequest(BaseModel):
    sso_key: str

class DecodeRequest(BaseModel):
    encode_content: str

class LdapAuthRequest(BaseModel):
    username: str
    password: str

def try_base64_decode(s: str):
    raw = base64.b64decode(s, validate=True)
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        try:
            return raw.decode("utf-8")
        except UnicodeDecodeError:
            return raw.hex()

# ======== API: Validate SSO ========
@app.post("/validate")
async def validate(req: ValidateRequest):
    url = f"{BASE_SSO_URL}{req.sso_key}"
    print(f"Validating SSO key: {req.sso_key} with URL: {url}")

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(url)
            resp.raise_for_status()
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=str(e))
    except httpx.HTTPError as e:
        raise HTTPException(status_code=502, detail=f"SSO upstream error: {e}")

    text_body = resp.text.strip()

    try:
        decoded = try_base64_decode(text_body)
        return {"ok": True, "decoded": decoded}
    except Exception as e:
        logging.exception("Decode failed: %s", e)
        return {"ok": False, "error": "Decode failed"}

# ======== API: Decode ========    
@app.post("/decode")
async def decode(req: DecodeRequest):
    try:
        decoded = try_base64_decode(req.encode_content)
        return {"ok": True, "decoded": decoded}
    except Exception as e:
        logging.exception("Decode failed: %s", e)
        return {"ok": False, "error": "Decode failed"}

# ======== API: LDAP SYNC  ========
@app.post("/ldap_sync")
async def ldap_sync(req: LdapAuthRequest):
    LDAP_SERVER = "ldap://192.168.171.43:389"
    LDAP_PASSWORD = req.password
    USER_DN = req.username
    BASE_DN = "DC=cdc,DC=gov,DC=tw"

    try:
        server = Server(LDAP_SERVER, get_info=ALL)
        conn = Connection(
            server,
            user=USER_DN,
            password=LDAP_PASSWORD,
            authentication=SIMPLE,
            auto_bind=True
        )

        conn.search(
            search_base=BASE_DN,
            search_filter="(&(objectClass=user)(!(userPrincipalName=*$)))",
            attributes=["sAMAccountName"]
        )

        accounts = []
        for entry in conn.entries:
            accounts.append({
                "account": entry.sAMAccountName.value,
                "name": entry.sAMAccountName.value,
                "password": "",
                "paddowrdmd5": "",
                "status": 1
            })

        conn.unbind()

        payload = {
            "header": {
                "txcode": "ACCOUNT_BATCH_INSERT",
                "usercode": None,
                "token": None,
                "appversion": "ldap_sync",
                "datetime": datetime.datetime.now().astimezone().isoformat()
            },
            "message": {
                "accounts": accounts
            }
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                "http://127.0.0.1:8080/ragapi/api/v1/tx",
                json=payload
            )
            resp.raise_for_status()
            result = resp.json()

        return {"ok": True, "inserted": len(accounts), "result": result}
    except Exception as e:
        logging.exception("LDAP Sync failed: %s", e)
        return {"ok": False, "error": "LDAP Sync Failed"}