# app/db.py

import os
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables from .env
load_dotenv()

SUPABASE_URL: str = os.getenv("SUPABASE_URL")
SUPABASE_KEY: str = os.getenv("SUPABASE_SERVICE_ROLE_KEY")  # use service role for backend

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("❌ Supabase credentials are not set in environment variables.")

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


def get_db_connection() -> Client:
    """
    Returns a Supabase client connection.
    """
    return supabase
