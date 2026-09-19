def format_recommendation(rec):
    return {
        "recommendation": rec["action"],
        "why_it_works": rec["why_it_works"],
        "impacted_metrics": rec["impacted_metrics"],
        "time_horizon": rec["time_horizon"],
        "confidence": rec["confidence"],
        "evidence": rec["evidence"],
        "measurement_plan": rec["measurement_plan"]
    }
