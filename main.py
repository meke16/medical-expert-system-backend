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


@app.get("/health")
def health():
    return {"status": "ok"}
