import os
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from clerk import Clerk

CLERK_API_KEY = os.getenv("CLERK_API_KEY")
clerk = Clerk(api_key=CLERK_API_KEY)

security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        # Verify the JWT via Clerk
        user = clerk.users.verify_jwt(token)
        
        # Extract role from public metadata
        role = user.get("public_metadata", {}).get("role")
        if not role:
            raise HTTPException(status_code=403, detail="Role not found in token")
        
        return {
            "id": user["id"],
            "email": user["email_addresses"][0]["email_address"],
            "role": role
        }
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Invalid or expired token: {str(e)}")

def require_role(user, role: str):
    if user.get("role") != role:
        raise HTTPException(status_code=403, detail=f"Access restricted to {role}s only")
