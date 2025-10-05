import hmac
from fastapi import Depends, HTTPException, status
from fastapi.security.api_key import APIKeyHeader
from .config import API_TOKEN

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

def verify_api_key(api_key: str = Depends(api_key_header)) -> bool:
    if not api_key or not hmac.compare_digest(api_key, API_TOKEN):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API token",
        )
    return True

