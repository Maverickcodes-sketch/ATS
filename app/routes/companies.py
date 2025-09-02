from fastapi import APIRouter, UploadFile, Depends
from app.auth import get_current_user,require_role
from app.db import get_db_connection
from app.embeddings import extract_text_from_pdf, generate_embedding

router = APIRouter()

@router.post("/upload-requirement")
def upload_requirement(file: UploadFile, user=Depends(get_current_user)):
    require_role(user, "company")
    owner_id = user["sub"]
    file_bytes = file.file.read()
    text = extract_text_from_pdf(file_bytes)
    embedding = generate_embedding(text)

    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO company_requirements (company_id, filename, text, embedding)
            SELECT c.id, %s, %s, %s
            FROM companies c
            WHERE c.owner_id = %s;
        """, (file.filename, text, embedding, owner_id))
        conn.commit()
    return {"status": "success", "message": "Requirement uploaded"}


from fastapi import APIRouter
from typing import Dict

router = APIRouter()

@router.get("/leaderboard/{job_id}")
def leaderboard(job_id: str):
    """
    Returns a leaderboard of all applicants for a job,
    sorted by score (descending), using your existing DB connection.
    """
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT candidate_id, score, probability
            FROM applications
            WHERE job_id = %s
            ORDER BY score DESC;
        """, (job_id,))
        results = cur.fetchall()

    leaderboard = [
        {
            "candidate_id": r[0],
            "score": round(r[1], 4),
            "probability_percent": round(r[2] if r[2] is not None else 0, 2)
        }
        for r in results
    ]

    return {
        "job_id": job_id,
        "leaderboard": leaderboard
    }


