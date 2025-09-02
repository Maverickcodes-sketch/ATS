import os
import json
import re
from typing import List, Dict
from fastapi import APIRouter, HTTPException, Depends
from app.auth import get_current_user,require_role
from app.db import get_db_connection

# ----------------------------
# Router
# ----------------------------
router = APIRouter()

# ----------------------------
# Load skills.json once
# ----------------------------
skills_file = os.path.join(os.path.dirname(__file__), "..", "skills.json")
with open(skills_file, "r", encoding="utf-8") as f:
    skill_course_dict = json.load(f)

# ----------------------------
# Skill Extraction Functions
# ----------------------------
def extract_skills_from_text(text: str) -> List[str]:
    """
    Extracts skills from given text based on keywords in skill_course_dict.
    """
    found_skills = []
    text_lower = text.lower()

    for skill in skill_course_dict.keys():
        if re.search(r"\b" + re.escape(skill.lower()) + r"\b", text_lower):
            found_skills.append(skill)

    return found_skills

def detect_skill_gap(resume_text: str, requirement_text: str) -> Dict[str, List[str]]:
    """
    Detects present, missing, and suggested courses for missing skills.
    """
    candidate_skills = extract_skills_from_text(resume_text)
    required_skills = extract_skills_from_text(requirement_text)

    missing_skills = set(required_skills) - set(candidate_skills)

    course_suggestions = {
        skill: skill_course_dict.get(skill, "No course available")
        for skill in missing_skills
    }

    return {
        "candidate_skills": candidate_skills,
        "required_skills": required_skills,
        "missing_skills": list(missing_skills),
        "course_suggestions": course_suggestions
    }

# ----------------------------
# API Endpoint
# ----------------------------
@router.get("/skill-gap/{job_id}/{candidate_id}")
async def skill_gap_api(job_id: str, candidate_id: str, user=Depends(get_current_user)):
    require_role(user, "candidate")
    """
    Fetch resume text and job requirement text from DB and detect skill gaps.
    """
    try:
        with get_db_connection() as conn:
            cur = conn.cursor()
            
            # Fetch candidate resume text
            cur.execute("""
                SELECT resume_text
                FROM candidates
                WHERE user_id = %s
            """, (candidate_id,))
            candidate_row = cur.fetchone()
            if not candidate_row:
                raise HTTPException(status_code=404, detail="Candidate not found")
            resume_text = candidate_row[0]

            # Fetch job requirement text
            cur.execute("""
                SELECT requirement_text
                FROM company_requirements
                WHERE id = %s
            """, (job_id,))
            job_row = cur.fetchone()
            if not job_row:
                raise HTTPException(status_code=404, detail="Job requirement not found")
            requirement_text = job_row[0]

        # Detect skill gap
        result = detect_skill_gap(resume_text, requirement_text)
        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

