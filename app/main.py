# app/main.py
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# # Import routers
from app import auth
from app.routes import candidates, companies, applications

# # Create FastAPI app
app = FastAPI(
    title="Internship Recommendation System",
    description="AI-powered matching of candidates and companies using Supabase + FastAPI",
    version="1.0.0"
)

# CORS Middleware (important for frontend access)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(candidates.router, prefix="/candidates", tags=["Candidates"])
app.include_router(companies.router, prefix="/companies", tags=["Companies"])
app.include_router(applications.router, prefix="/applications", tags=["Applications"])

# Root endpoint
@app.get("/")
def root():
    return {"message": "Internship Recommendation System API is running 🚀"}
