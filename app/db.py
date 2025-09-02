# db.py

from supabase import create_client, Client
import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

SUPABASE_URL: str = os.getenv("SUPABASE_URL")
SUPABASE_KEY: str = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Supabase credentials are not set in environment variables.")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def get_db_connection() -> Client:
    """
    Returns a Supabase client connection.
    """
    return supabase
