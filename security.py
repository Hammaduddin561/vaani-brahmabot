# security.py

from fastapi import HTTPException, Security
from fastapi.security.api_key import APIKeyHeader

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv(override=True)

# Your internal API key for /chat endpoint from .env
# IMPORTANT: Set API_KEY in your .env file for security
API_KEY        = os.getenv("API_KEY", "demo-key-change-in-production")
API_KEY_HEADER = APIKeyHeader(name="X-API-KEY")

def get_api_key(api_key: str = Security(API_KEY_HEADER)):
    if api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")
    return api_key