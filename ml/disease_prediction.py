def convert_to_number(value):
    """
    Convert values such as:
    '11.2', '13,200', 168 or 180000
    into float values safely.
    """

    if value is None:
        return None

    try:
        cleaned_value = str(value).replace(",", "").strip()
        return float(cleaned_value)

    except (TypeError, ValueError):
        return None


def predict_disease(parameters):

    diseases = []

    hemoglobin = convert_to_number(
        parameters.get("Hemoglobin")
    )

    blood_sugar = convert_to_number(
        parameters.get("Blood Sugar")
    )

    wbc = convert_to_number(
        parameters.get("WBC")
    )

    platelets = convert_to_number(
        parameters.get("Platelets")
    )

    # Possible anemia
    if hemoglobin is not None and hemoglobin < 13.0:
        diseases.append(
            {
                "Disease": "Possible Anemia",
                "Probability": "90%"
            }
        )

    # Possible diabetes
    if blood_sugar is not None and blood_sugar > 126.0:
        diseases.append(
            {
                "Disease": "Possible Diabetes",
                "Probability": "95%"
            }
        )

    # Possible infection
    if wbc is not None and wbc > 11000.0:
        diseases.append(
            {
                "Disease": "Possible Infection",
                "Probability": "88%"
            }
        )

    # Possible low platelet condition
    if platelets is not None and platelets < 150000.0:
        diseases.append(
            {
                "Disease": "Possible Low Platelet Condition",
                "Probability": "85%"
            }
        )

    return diseases