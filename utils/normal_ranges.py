# =====================================================
# General Adult Reference Ranges
# Educational defaults only
# =====================================================

NORMAL_RANGES = {
    # Complete Blood Count
    "Hemoglobin": (12.0, 17.0),       # g/dL
    "RBC": (4.0, 6.1),                # million cells/cu.mm
    "HCT": (36.0, 55.0),              # %
    "MCV": (80.0, 100.0),             # fL
    "MCH": (27.0, 32.0),              # pg
    "MCHC": (32.0, 36.0),             # g/dL
    "WBC": (4000.0, 11000.0),         # cells/cu.mm
    "Platelets": (150000.0, 400000.0),# cells/cu.mm

    # Differential Count
    "Neutrophils": (40.0, 70.0),      # %
    "Lymphocytes": (20.0, 45.0),      # %
    "Monocytes": (2.0, 10.0),         # %
    "Eosinophils": (1.0, 6.0),        # %
    "Basophils": (0.0, 2.0),          # %

    # ESR
    # Simple educational default only.
    # ESR varies significantly with age, sex and testing method.
    "ESR": (0.0, 20.0),               # mm/hour

    # Blood Sugar
    "Blood Sugar": (70.0, 126.0),     # mg/dL
}


def convert_to_float(value):
    """
    Safely convert values such as:
    12.5
    "12.5 g/dL"
    "150,000"
    "04"
    into float values.
    """

    if value is None:
        return None

    try:
        cleaned_value = str(value).replace(",", "").strip()

        number = ""
        decimal_found = False
        negative_found = False

        for character in cleaned_value:

            if character.isdigit():
                number += character

            elif character == "." and not decimal_found:
                number += character
                decimal_found = True

            elif (
                character == "-"
                and not negative_found
                and not number
            ):
                number += character
                negative_found = True

            elif number:
                break

        if number in ["", ".", "-", "-."]:
            return None

        return float(number)

    except (TypeError, ValueError):
        return None


def check_normal_ranges(parameters):
    """
    Compare extracted parameters with general reference ranges.

    Returns:
        {
            "Parameter": {
                "Value": numeric_value,
                "Minimum": minimum,
                "Maximum": maximum,
                "Status": "Low" | "Normal" | "High"
            }
        }
    """

    results = {}

    if not isinstance(parameters, dict):
        return results

    for parameter, value in parameters.items():

        numeric_value = convert_to_float(value)

        if numeric_value is None:
            results[parameter] = {
                "Value": value,
                "Minimum": None,
                "Maximum": None,
                "Status": "Invalid value"
            }
            continue

        if parameter not in NORMAL_RANGES:
            results[parameter] = {
                "Value": numeric_value,
                "Minimum": None,
                "Maximum": None,
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
            "Minimum": minimum,
            "Maximum": maximum,
            "Status": status
        }

    return results