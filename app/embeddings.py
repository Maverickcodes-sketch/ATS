from sentence_transformers import SentenceTransformer
import fitz  # PyMuPDF

model = SentenceTransformer("all-MiniLM-L6-v2")

def extract_text_from_pdf(file_bytes: bytes) -> str:
    doc = fitz.open("pdf", file_bytes)
    text = ""
    for page in doc:
        text += page.get_text()
    return text

def generate_embedding(text: str):
    return model.encode([text])[0].tolist()
