def suggest_specialists(range_results):

    specialists = []

    if "Hemoglobin" in range_results:
        if range_results["Hemoglobin"]["Status"] == "Low":
            specialists.append("🩸 Hematologist")

    if "Blood Sugar" in range_results:
        if range_results["Blood Sugar"]["Status"] == "High":
            specialists.append("🍬 Diabetologist")

    if "WBC" in range_results:
        if range_results["WBC"]["Status"] == "High":
            specialists.append("🩺 General Physician")

    if "Platelets" in range_results:
        if range_results["Platelets"]["Status"] == "Low":
            specialists.append("🩸 Hematologist")

    if not specialists:
        specialists.append(
            "✅ General Physician (Routine Check-up)"
        )

    # Remove duplicate specialists while preserving order
    specialists = list(dict.fromkeys(specialists))

    return specialists