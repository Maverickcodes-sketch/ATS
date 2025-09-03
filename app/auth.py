import os
from dotenv import load_dotenv
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from clerk_backend_api import Clerk

# ================================
# Load environment variables
# ================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_PATH = os.path.join(BASE_DIR, ".env")
load_dotenv(ENV_PATH)


# ================================
# Clerk setup
# ================================
CLERK_API_KEY = os.getenv("CLERK_API_KEY")
print("DEBUG: CLERK_API_KEY loaded:", CLERK_API_KEY[:5] + "..." if CLERK_API_KEY else "❌ NOT FOUND")

if not CLERK_API_KEY:
    raise ValueError("❌ CLERK_API_KEY is missing. Please set it in app/.env")

clerk = Clerk()

# ================================
# Security for FastAPI
# ================================
security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Verify the session token with Clerk and return the user object with role.
    """
    token = credentials.credentials
    try:
        # Verify session
        session = clerk.sessions.verify(token)
        user_id = session.user_id

        # Fetch user
        user = clerk.users.get_user(user_id)

        role = user.public_metadata.get("role")
        if not role:
            raise HTTPException(status_code=403, detail="Role not found in Clerk public_metadata")

        return {
            "id": user.id,
            "email": user.email_addresses[0].email_address if user.email_addresses else "unknown",
            "role": role
        }

    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Invalid or expired token: {str(e)}")


def require_role(user, role: str):
    """
    Restrict access to routes by role.
    Example:
        @router.get("/companies-only")
        def read_companies(user=Depends(get_current_user)):
            require_role(user, "company")
            return {"message": "Welcome company!"}
    """
    if user.get("role") != role:
        raise HTTPException(status_code=403, detail=f"Access restricted to {role}s only")
