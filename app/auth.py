import os
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt

SUPABASE_JWT_SECRET = os.getenv("SUPABASE_JWT_SECRET")

security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SUPABASE_JWT_SECRET, algorithms=["HS256"])
        return payload   # { "sub": user_id, "email": ... }
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
