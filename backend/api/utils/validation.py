"""Validation of the structured, non-diagnostic report representation."""

REQUIRED_RESULT_FIELDS = {"test_name", "value", "unit", "min_range", "max_range", "status"}
VALID_STATUSES = {"NORMAL", "HIGH", "LOW", "UNKNOWN"}


def validate_report_data(document_type, results, summary, extracted_text):
    """Return machine-readable schema, consistency, and quality validation."""
    errors = []
    warnings = []

    if not isinstance(results, list):
        errors.append("results must be a list")
        results = []
    if not isinstance(summary, dict):
        errors.append("summary must be an object")
        summary = {}

    for index, result in enumerate(results):
        missing = sorted(REQUIRED_RESULT_FIELDS - set(result))
        if missing:
            errors.append(f"results[{index}] missing: {', '.join(missing)}")
        if result.get("status") not in VALID_STATUSES:
            errors.append(f"results[{index}] has an invalid status")
        try:
            float(result.get("value"))
        except (TypeError, ValueError):
            errors.append(f"results[{index}] value is not numeric")

    expected_summary = {
        "total_tests": len(results),
        "normal": sum(1 for result in results if result.get("status") == "NORMAL"),
        "high": sum(1 for result in results if result.get("status") == "HIGH"),
        "low": sum(1 for result in results if result.get("status") == "LOW"),
    }
    for key, expected in expected_summary.items():
        if summary.get(key) != expected:
            errors.append(f"summary.{key} does not match results")

    if document_type in {"MRI", "CT", "X-ray", "ECG", "Discharge Summary", "Clinical Notes"} and not results:
        warnings.append("This document type is preserved as text; lab-value extraction is not applicable")
    if not extracted_text or len(extracted_text.strip()) < 40:
        warnings.append("Very little readable text was extracted")

    return {
        "schema_valid": not errors,
        "errors": errors,
        "warnings": warnings,
        "required_fields": sorted(REQUIRED_RESULT_FIELDS),
        "non_diagnostic": True,
    }
