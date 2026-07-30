import re


NORMAL_RANGES = {
    "Hemoglobin": (13.0, 17.0),
    "WBC": (4000.0, 11000.0),
    "RBC": (4.5, 6.0),
    "Platelets": (150000.0, 450000.0),
    "Blood Sugar": (70.0, 126.0)
}


def convert_to_float(value):
    """Safely convert extracted text into a number."""

    if value is None:
        return None

    try:
        cleaned_value = str(value).replace(",", "").strip()
        return float(cleaned_value)

    except (TypeError, ValueError):
        return None


# -------------------------------------
# Extract Medical Parameters
# -------------------------------------
def extract_parameters(report_text):

    parameters = {}

    patterns = {
        "Hemoglobin": r"Hemoglobin\s*[:\-]?\s*([\d.]+)",
        "WBC": r"WBC\s*[:\-]?\s*([\d,]+)",
        "RBC": r"RBC\s*[:\-]?\s*([\d.]+)",
        "Platelets": r"Platelets\s*[:\-]?\s*([\d,]+)",
        "Blood Sugar": r"Blood Sugar\s*[:\-]?\s*([\d.]+)"
    }

    for parameter, pattern in patterns.items():

        match = re.search(
            pattern,
            report_text,
            re.IGNORECASE
        )

        if match:

            numeric_value = convert_to_float(match.group(1))

            if numeric_value is not None:
                parameters[parameter] = numeric_value

    return parameters


# -------------------------------------
# Check Normal Ranges
# -------------------------------------
def check_normal_ranges(parameters):

    results = {}

    for parameter, value in parameters.items():

        numeric_value = convert_to_float(value)

        if numeric_value is None:
            results[parameter] = {
                "Value": value,
                "Status": "Invalid"
            }
            continue

        if parameter not in NORMAL_RANGES:
            results[parameter] = {
                "Value": numeric_value,
                "Status": "Range not available"
            }
            continue

        minimum, maximum = NORMAL_RANGES[parameter]

        if numeric_value < minimum:
            status = "Low"

        elif numeric_value > maximum:
            status = "High"

        else:
            status = "Normal"

        results[parameter] = {
            "Value": numeric_value,
            "Status": status
        }

    return results