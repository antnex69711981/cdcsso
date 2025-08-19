from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import httpx
import base64
import json
import logging

app = FastAPI()

logging.basicConfig(level=logging.INFO)
BASE_SSO_URL = "http://192.168.171.27:8080/api/values/CheckKey?SSOkey="

class ValidateRequest(BaseModel):
    sso_key: str

class DecodeRequest(BaseModel):
    encode_content: str

def try_base64_decode(s: str):
    raw = base64.b64decode(s, validate=True)
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        try:
            return raw.decode("utf-8")
        except UnicodeDecodeError:
            return raw.hex()

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
    
@app.post("/decode")
async def decode(req: DecodeRequest):
    try:
        decoded = try_base64_decode(req.encode_content)
        return {"ok": True, "decoded": decoded}
    except Exception as e:
        logging.exception("Decode failed: %s", e)
        return {"ok": False, "error": "Decode failed"}
    