from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from engine.diagnosis import diagnose, ALL_SYMPTOMS

app = FastAPI(title="Medical Diagnosis Expert System")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class DiagnoseRequest(BaseModel):
    symptoms: list[str] = Field(..., min_length=1)
    age: int = Field(..., ge=1, le=120)
    gender: str = Field(..., pattern="^(male|female|other)$")
    lang: str = Field(default="en", pattern="^(en|am|om)$")


class ReportRequest(BaseModel):
    patient: dict
    symptoms: list[str]
    results: list[dict]


ABOUT_INFO = {
    "system_name": "AI-Powered Medical Decision Support System",
    "summary": (
        "An AI-style medical decision support system that ranks likely conditions "
        "from user-reported symptoms, age, gender, and the selected language. "
        "The implementation is rule-based and uses a static knowledge base."
    ),
    "algorithm": {
        "type": "Weighted symptom matching",
        "steps": [
            "Load the static disease knowledge base from backend/data/diseases.json at import time.",
            "Find diseases that share at least one symptom with the user selection.",
            "Score each disease using symptom coverage and symptom overlap.",
            "Adjust the score with age-group and gender risk multipliers.",
            "Sort matches by final confidence and return the top 5 results.",
        ],
        "formula": "raw_confidence = (0.7 * symptom_overlap) + (0.3 * symptom_coverage)",
        "score_notes": [
            "Confidence is capped below 100% so the output is always a ranked suggestion, not a certainty.",
            "There is no machine learning model, probabilistic network, or external medical API involved.",
        ],
    },
    "data_flow": {
        "frontend": [
            "The diagnosis page fetches /api/symptoms to render the selectable symptom list.",
            "The frontend filters symptom labels locally as the user types in the search box.",
            "When the user submits, the frontend sends symptoms, age, gender, and lang to /api/diagnose.",
            "The results page can re-request the diagnosis in another language when lang changes.",
        ],
        "backend": [
            "The backend keeps the disease knowledge base in memory after startup.",
            "Each request is processed in memory and nothing is written to a database.",
            "Localization falls back to English if a disease translation is missing for the requested language.",
        ],
    },
    "knowledge_base": {
        "source": "backend/data/diseases.json",
        "fields": [
            "id",
            "name and localized names",
            "severity",
            "symptoms",
            "explanation and localized explanations",
            "treatment and localized treatment guidance",
            "age_risk modifiers",
            "gender_risk modifiers",
        ],
    },
    "api": [
        "/health",
        "/api/symptoms",
        "/api/diagnose",
        "/api/report",
        "/api/about",
    ],
    "faq": [
        {
            "question": "Is this an AI/ML model?",
            "answer": "It is AI-style decision support, but not machine learning. It uses a rule-based inference engine with a curated JSON knowledge base.",
        },
        {
            "question": "Why does the same symptom list produce different results for different users?",
            "answer": "Age group and gender risk multipliers change the final confidence score, so the ranking can shift.",
        },
        {
            "question": "Why are there only up to 5 results?",
            "answer": "The engine returns the top 5 highest-confidence matches to keep the output focused and readable.",
        },
        {
            "question": "Where is the data stored?",
            "answer": "The static medical data lives in backend/data/diseases.json and is loaded into memory on startup.",
        },
        {
            "question": "Can I trust the output as a diagnosis?",
            "answer": "No. It is an educational tool only and should be used as a guide, not a clinical diagnosis.",
        },
    ],
}


@app.get("/api/symptoms")
def get_symptoms():
    return {"symptoms": ALL_SYMPTOMS}


@app.get("/api/about")
def get_about():
    return ABOUT_INFO


@app.post("/api/diagnose")
def run_diagnosis(req: DiagnoseRequest):
    if not req.symptoms:
        raise HTTPException(status_code=400, detail="At least one symptom required")
    results = diagnose(req.symptoms, req.age, req.gender, req.lang)
    return {
        "patient": {"age": req.age, "gender": req.gender},
        "symptoms": req.symptoms,
        "results": results,
    }


@app.post("/api/report")
def generate_report(req: ReportRequest):
    from datetime import datetime
    return {
        "report": {
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "patient": req.patient,
            "symptoms": req.symptoms,
            "top_diagnosis": req.results[0] if req.results else None,
            "all_results": req.results,
        }
    }


@app.get("/health")
def health():
    return {"status": "ok"}
