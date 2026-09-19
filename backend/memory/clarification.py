def clarification_message(missing_fields):
    if not missing_fields:
        return None
    return "To make the assessment evidence-specific, please provide: " + ", ".join(missing_fields) + "."
