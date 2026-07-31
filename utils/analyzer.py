import re


def _clean_number(value):
    """
    Convert OCR-style numeric text into a float.

    Examples:
    8,300 -> 8300
    04 -> 4
    Ol -> 1
    25.7 -> 25.7
    """
    if value is None:
        return None

    cleaned = str(value).strip()

    # Fix common OCR number mistakes
    cleaned = cleaned.replace(",", "")
    cleaned = cleaned.replace("O", "0")
    cleaned = cleaned.replace("o", "0")
    cleaned = cleaned.replace("I", "1")
    cleaned = cleaned.replace("l", "1")
    cleaned = cleaned.replace("|", "1")

    match = re.search(r"-?\d+(?:\.\d+)?", cleaned)

    if not match:
        return None

    try:
        return float(match.group())
    except ValueError:
        return None


def _find_value(text, patterns):
    """
    Try multiple regular-expression patterns and return
    the first valid numeric value found.
    """
    for pattern in patterns:
        match = re.search(
            pattern,
            text,
            flags=re.IGNORECASE | re.MULTILINE,
        )

        if match:
            value = _clean_number(match.group(1))

            if value is not None:
                return value

    return None


def extract_parameters(text):
    """
    Extract medical parameters from normal text PDFs and
    OCR-generated text from scanned blood reports.
    """
    if not text:
        return {}

    # Improve OCR text consistency
    cleaned_text = str(text)
    cleaned_text = cleaned_text.replace("–", "-")
    cleaned_text = cleaned_text.replace("—", "-")
    cleaned_text = cleaned_text.replace("\t", " ")

    parameters = {}

    hemoglobin = _find_value(
        cleaned_text,
        [
            r"\bHEMOGLOBIN\b\s*[:\-]?\s*(\d+(?:\.\d+)?)",
            r"\bHAEMOGLOBIN\b\s*[:\-]?\s*(\d+(?:\.\d+)?)",
            r"\bHB\b\s*[:\-]?\s*(\d+(?:\.\d+)?)",
        ],
    )

    rbc = _find_value(
        cleaned_text,
        [
            r"\bRBC\s*COUNT\b\s*[:\-]?\s*(\d+(?:\.\d+)?)",
            r"\bRBC\b\s*[:\-]?\s*(\d+(?:\.\d+)?)",
        ],
    )

    hct = _find_value(
        cleaned_text,
        [
            r"\bHCT\b\s*[:\-]?\s*(\d+(?:\.\d+)?)",
            r"\bPCV\b\s*[:\-]?\s*(\d+(?:\.\d+)?)",
        ],
    )

    mcv = _find_value(
        cleaned_text,
        [r"\bMCV\b\s*[:\-]?\s*(\d+(?:\.\d+)?)"],
    )

    mch = _find_value(
        cleaned_text,
        [r"\bMCH\b(?!C)\s*[:\-]?\s*(\d+(?:\.\d+)?)"],
    )

    # OCR may read 25.7 as 257
    if mch is not None and 100 <= mch <= 999:
        mch = mch / 10

    mchc = _find_value(
        cleaned_text,
        [r"\bMCHC\b\s*[:\-]?\s*(\d+(?:\.\d+)?)"],
    )

    wbc = _find_value(
        cleaned_text,
        [
            r"\bTWBC\s*COUNT\b\s*[:\-]?\s*([\d,]+(?:\.\d+)?)",
            r"\bTOTAL\s*WBC\s*COUNT\b\s*[:\-]?\s*([\d,]+(?:\.\d+)?)",
            r"\bWBC\s*COUNT\b\s*[:\-]?\s*([\d,]+(?:\.\d+)?)",
            r"\bWBC\b\s*[:\-]?\s*([\d,]+(?:\.\d+)?)",
        ],
    )

    platelets = _find_value(
        cleaned_text,
        [
            r"\bPLATELET\s*COUNT\b\s*[:\-]?\s*(\d+(?:\.\d+)?)",
            r"\bPLATELETS?\b\s*[:\-]?\s*(\d+(?:\.\d+)?)",
        ],
    )

    # Convert lakh-based platelet value:
    # 3.53 lakhs/cu.mm -> 353000 cells/cu.mm
    platelet_line = re.search(
        r"\bPLATELET\s*COUNT\b[^\n]*",
        cleaned_text,
        flags=re.IGNORECASE,
    )

    if (
        platelets is not None
        and platelet_line
        and re.search(
            r"lakh|lakhs|takhs",
            platelet_line.group(),
            flags=re.IGNORECASE,
        )
    ):
        platelets = platelets * 100000

    esr = _find_value(
        cleaned_text,
        [r"\bESR\b\s*[:\-]?\s*(\d+(?:\.\d+)?)"],
    )

    neutrophils = _find_value(
        cleaned_text,
        [r"\bNEUTROPHILS?\b\s*[:\-]?\s*([0-9OolI|]+(?:\.\d+)?)"],
    )

    lymphocytes = _find_value(
        cleaned_text,
        [r"\bLYMPHOCYTES?\b\s*[:\-]?\s*([0-9OolI|]+(?:\.\d+)?)"],
    )

    monocytes = _find_value(
        cleaned_text,
        [r"\bMONOCYTES?\b\s*[:\-]?\s*([0-9OolI|]+(?:\.\d+)?)"],
    )

    eosinophils = _find_value(
        cleaned_text,
        [r"\bEOSINOPHILS?\b\s*[:\-]?\s*([0-9OolI|]+(?:\.\d+)?)"],
    )

    extracted = {
        "Hemoglobin": hemoglobin,
        "RBC": rbc,
        "HCT": hct,
        "MCV": mcv,
        "MCH": mch,
        "MCHC": mchc,
        "WBC": wbc,
        "Platelets": platelets,
        "ESR": esr,
        "Neutrophils": neutrophils,
        "Lymphocytes": lymphocytes,
        "Monocytes": monocytes,
        "Eosinophils": eosinophils,
    }

    # Remove parameters that OCR could not read
    return {
        name: value
        for name, value in extracted.items()
        if value is not None
    }