from fastapi import Header, HTTPException
import os

def verify_api_key(x_api_key: str = Header(..., alias="x-api-key")):
    if x_api_key != os.getenv("EXTENSION_API_KEY"):
        raise HTTPException(status_code=403, detail="Invalid API key")
