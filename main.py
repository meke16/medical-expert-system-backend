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


@app.get("/api/symptoms")
def get_symptoms():
    return {"symptoms": ALL_SYMPTOMS}


@app.post("/api/diagnose")
def run_diagnosis(req: DiagnoseRequest):
    if not req.symptoms:
        raise HTTPException(status_code=400, detail="At least one symptom required")
    results = diagnose(req.symptoms, req.age, req.gender)
    return {
        "patient": {"age": req.age, "gender": req.gender},
        "symptoms": req.symptoms,
        "results": results,
    }


class ReportRequest(BaseModel):
    patient: dict
    symptoms: list[str]
    results: list[dict]


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
