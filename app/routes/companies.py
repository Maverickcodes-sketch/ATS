from fastapi import APIRouter, UploadFile, Depends
from app.auth import get_current_user
from app.db import get_db_connection
from app.embeddings import extract_text_from_pdf, generate_embedding

router = APIRouter()

@router.post("/upload-requirement")
def upload_requirement(file: UploadFile, user=Depends(get_current_user)):
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


@router.get("/recommend-candidates")
def recommend_candidates(top_n: int = 5, user=Depends(get_current_user)):
    owner_id = user["sub"]

    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT cand.user_id, cand.full_name, cand.email, 1 - (cand.resume_embedding <=> cr.embedding) AS similarity
            FROM company_requirements cr
            JOIN companies comp ON comp.id = cr.company_id
            JOIN candidates cand ON TRUE
            WHERE comp.owner_id = %s
            ORDER BY similarity DESC
            LIMIT %s;
        """, (owner_id, top_n))
        results = cur.fetchall()

    return [
        {"candidate_id": r[0], "name": r[1], "email": r[2], "score": float(r[3])}
        for r in results
    ]

