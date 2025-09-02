from fastapi import APIRouter, Depends
from app.auth import get_current_user,require_role
from app.db import get_db_connection

router = APIRouter()

@router.post("/apply/{company_id}")
def apply(company_id: int, user=Depends(get_current_user)):
    require_role(user, "company")
    candidate_id = user["sub"]
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO applications (candidate_id, company_id, status)
            VALUES (%s, %s, 'applied')
            ON CONFLICT DO NOTHING;
        """, (candidate_id, company_id))
        conn.commit()
    return {"status": "success", "message": "Applied successfully"}

@router.post("/shortlist/{candidate_id}")
def shortlist(candidate_id: str, user=Depends(get_current_user)):
    require_role(user, "company")
    owner_id = user["sub"]
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute("""
            UPDATE applications
            SET status = 'shortlisted'
            WHERE candidate_id = %s
              AND company_id IN (SELECT id FROM companies WHERE owner_id = %s);
        """, (candidate_id, owner_id))
        conn.commit()
    return {"status": "success", "message": "Candidate shortlisted"}
