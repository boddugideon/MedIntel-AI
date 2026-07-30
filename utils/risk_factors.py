def detect_risk_factors(range_results):

    risks = []

    if "Hemoglobin" in range_results:
        if range_results["Hemoglobin"]["Status"] == "Low":
            risks.append("🩸 Possible Anemia")

    if "Blood Sugar" in range_results:
        if range_results["Blood Sugar"]["Status"] == "High":
            risks.append("🍬 Possible Diabetes")

    if "WBC" in range_results:
        if range_results["WBC"]["Status"] == "High":
            risks.append("🦠 Possible Infection")

    if "Platelets" in range_results:
        if range_results["Platelets"]["Status"] == "Low":
            risks.append(
                "🩹 Possible Low Platelet Condition"
            )

    return risks