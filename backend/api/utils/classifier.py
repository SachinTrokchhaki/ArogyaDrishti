"""Deterministic document type classification for report routing."""
import re


DOCUMENT_TYPES = (
    "CBC",
    "Biochemistry",
    "MRI",
    "CT",
    "X-ray",
    "ECG",
    "Prescription",
    "Discharge Summary",
    "Clinical Notes",
    "Other",
)

KEYWORDS = {
    "CBC": ("hemoglobin", "leucocyte", "neutrophils", "platelet", "cbc", "rbc count"),
    "Biochemistry": ("creatinine", "bilirubin", "cholesterol", "glucose", "albumin", "liver function"),
    "MRI": ("magnetic resonance", "mri", "t1", "t2", "diffusion", "impression"),
    "CT": ("computed tomography", "ct scan", "contrast enhanced", "hounsfield"),
    "X-ray": ("x-ray", "xray", "radiograph", "radiology"),
    "ECG": ("electrocardiogram", "ecg", "ekg", "pr interval", "qrs", "st segment"),
    "Prescription": ("prescription", "tablet", "capsule", "dosage", "prescribed", "rx"),
    "Discharge Summary": ("discharge summary", "discharged", "admission date", "discharge date"),
    "Clinical Notes": ("chief complaint", "history of present illness", "clinical notes", "assessment", "plan"),
}


def classify_document(text):
    normalized = re.sub(r"\s+", " ", (text or "").lower())
    scores = {
        document_type: sum(normalized.count(keyword) for keyword in keywords)
        for document_type, keywords in KEYWORDS.items()
    }
    best_type, best_score = max(scores.items(), key=lambda item: item[1])
    if best_score == 0:
        return {"document_type": "Other", "confidence": 0, "scores": scores}

    total_score = sum(scores.values()) or 1
    confidence = min(99, round(55 + (best_score / total_score) * 44))
    return {
        "document_type": best_type,
        "confidence": confidence,
        "scores": scores,
    }
