from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import pdfplumber

app = FastAPI()

# CORS for frontend (voice UI)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def health():
    return {"status": "Sahayak backend is running"}

@app.post("/parse-form")
async def parse_form(file: UploadFile = File(...)):
    extracted_fields = []

    # Only handle PDFs safely on Render free tier
    if not file.filename.lower().endswith(".pdf"):
        return {
            "success": False,
            "message": "Only PDF forms are supported"
        }

    try:
        with pdfplumber.open(file.file) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if not text:
                    continue

                for line in text.split("\n"):
                    # Simple, safe heuristic for form fields
                    if ":" in line:
                        field = line.split(":")[0].strip()
                        if len(field) > 2:
                            extracted_fields.append(field)

        return {
            "success": True,
            "fields": extracted_fields
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
