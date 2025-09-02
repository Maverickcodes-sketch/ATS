from fastapi import APIRouter, UploadFile, Depends, HTTPException
from app.auth import get_current_user,require_role
from app.db import get_db_connection
from app.embeddings import extract_text_from_pdf, generate_embedding

router = APIRouter()

@router.post("/upload-resume")
def upload_resume(file: UploadFile, user=Depends(get_current_user)):
    require_role(user, "candidate")
    user_id = user["sub"]
    file_bytes = file.file.read()
    text = extract_text_from_pdf(file_bytes)
    embedding = generate_embedding(text)

    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO candidates (user_id, resume_filename, resume_text, resume_embedding)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (user_id) DO UPDATE
              SET resume_filename = EXCLUDED.resume_filename,
                  resume_text = EXCLUDED.resume_text,
                  resume_embedding = EXCLUDED.resume_embedding;
        """, (user_id, file.filename, text, embedding))
        conn.commit()
    return {"status": "success", "message": "Resume uploaded"}

@router.get("/recommend-companies")
def recommend_companies(top_n: int = 5, user=Depends(get_current_user)):
    require_role(user, "candidate")
    user_id = user["sub"]

    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT c.id, c.name, cr.filename, 1 - (cand.resume_embedding <=> cr.embedding) AS similarity
            FROM candidates cand
            JOIN company_requirements cr ON TRUE
            JOIN companies c ON c.id = cr.company_id
            WHERE cand.user_id = %s
            ORDER BY similarity DESC
            LIMIT %s;
        """, (user_id, top_n))
        results = cur.fetchall()

    return [
        {"company_id": r[0], "company_name": r[1], "requirement_file": r[2], "score": float(r[3])}
        for r in results
    ]

