NORMAL_RANGES = {
    "Hemoglobin": (13.0, 17.0),
    "WBC": (4000, 11000),
    "RBC": (4.5, 6.0),
    "Platelets": (150000, 450000),
    "Blood Sugar": (70, 126)
}


def convert_to_float(value):
    """
    Safely convert extracted values such as
    '12.5', '12.5 g/dL', or '150,000' into numbers.
    """

    if value is None:
        return None

    try:
        cleaned_value = str(value).replace(",", "").strip()

        number = ""

        for character in cleaned_value:
            if character.isdigit() or character in [".", "-"]:
                number += character
            elif number:
                break

        if not number or number in [".", "-", "-."]:
            return None

        return float(number)

    except (TypeError, ValueError):
        return None


def check_normal_ranges(parameters):

    results = {}

    for parameter, value in parameters.items():

        numeric_value = convert_to_float(value)

        if numeric_value is None:
            results[parameter] = {
                "Value": value,
                "Status": "Invalid value"
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