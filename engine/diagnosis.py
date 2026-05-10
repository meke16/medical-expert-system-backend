import json
from pathlib import Path

with open(Path(__file__).parent.parent / "data" / "diseases.json") as f:
    DISEASES = json.load(f)

ALL_SYMPTOMS = sorted({s for d in DISEASES for s in d["symptoms"]})


def get_age_group(age: int) -> str:
    if age < 18:
        return "child"
    elif age < 60:
        return "adult"
    return "senior"


def localized(disease: dict, field: str, lang: str) -> str:
    key = f"{field}_{lang}"
    return disease.get(key) or disease.get(field, "")


def diagnose(symptoms: list[str], age: int, gender: str, lang: str = "en") -> list[dict]:
    age_group = get_age_group(age)
    results = []

    for disease in DISEASES:
        matched = [s for s in symptoms if s in disease["symptoms"]]
        if not matched:
            continue

        base_score = len(matched) / len(disease["symptoms"])
        coverage = len(matched) / len(symptoms) if symptoms else 0
        raw_confidence = (base_score * 0.7 + coverage * 0.3)

        age_mod = disease["age_risk"].get(age_group, 1.0)
        gender_mod = disease["gender_risk"].get(gender.lower(), 1.0)
        confidence = min(raw_confidence * age_mod * gender_mod, 0.99)

        results.append({
            "id": disease["id"],
            "name": localized(disease, "name", lang),
            "severity": disease["severity"],
            "confidence": round(confidence * 100, 1),
            "matched_symptoms": matched,
            "total_symptoms": len(disease["symptoms"]),
            "explanation": localized(disease, "explanation", lang),
            "treatment": localized(disease, "treatment", lang),
        })

    results.sort(key=lambda x: x["confidence"], reverse=True)
    return results[:5]
