def detect_risk_factors(range_results):

    risks = []

    # Helper function
    def status(parameter):
        if parameter in range_results:
            return range_results[parameter]["Status"]
        return None

    # =====================================================
    # Iron Deficiency Anemia
    # =====================================================
    if (
        status("Hemoglobin") == "Low"
        or (
            status("MCV") == "Low"
            and status("MCH") == "Low"
        )
    ):
        risks.append(
            "🩸 Possible Iron Deficiency Anemia (Low Hemoglobin / Low MCV + Low MCH)"
        )

    # =====================================================
    # Infection
    # =====================================================
    if (
        status("WBC") == "High"
        and status("Neutrophils") == "High"
    ):
        risks.append(
            "🦠 Possible Bacterial Infection (High WBC + High Neutrophils)"
        )

    # =====================================================
    # Viral Infection
    # =====================================================
    if (
        status("Neutrophils") == "Low"
        and status("Lymphocytes") == "High"
    ):
        risks.append(
            "🦠 Possible Viral Infection (Low Neutrophils + High Lymphocytes)"
        )

    # =====================================================
    # High ESR
    # =====================================================
    if status("ESR") == "High":
        risks.append(
            "🔥 High ESR detected (Possible inflammation or infection)"
        )

    # =====================================================
    # Neutropenia
    # =====================================================
    if status("Neutrophils") == "Low":
        risks.append(
            "🩸 Mild Neutropenia (Low Neutrophil count)"
        )

    # =====================================================
    # Thrombocytopenia
    # =====================================================
    if status("Platelets") == "Low":
        risks.append(
            "🩹 Possible Thrombocytopenia (Low Platelet count)"
        )

    # =====================================================
    # Diabetes
    # =====================================================
    if status("Blood Sugar") == "High":
        risks.append(
            "🍬 Possible Diabetes (High Blood Sugar)"
        )

    # =====================================================
    # Eosinophilia
    # =====================================================
    if status("Eosinophils") == "High":
        risks.append(
            "🌿 Possible Allergy / Parasitic Infection (High Eosinophils)"
        )

    # =====================================================
    # No risks
    # =====================================================
    if len(risks) == 0:
        risks.append("✅ No major clinical risks detected.")

    return risks