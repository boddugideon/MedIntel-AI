from io import BytesIO
import platform

import fitz
import pytesseract
from PIL import Image


# Use the Windows Tesseract path only on your local Windows computer.
# On Streamlit Cloud/Linux, Tesseract is found automatically from packages.txt.
if platform.system() == "Windows":
    pytesseract.pytesseract.tesseract_cmd = (
        r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    )


def extract_text_with_ocr(uploaded_file):
    """
    Extract text from scanned or image-based PDF files using OCR.
    Returns extracted text as a string.
    """

    pdf_document = None

    try:
        uploaded_file.seek(0)
        pdf_bytes = uploaded_file.read()

        pdf_document = fitz.open(
            stream=pdf_bytes,
            filetype="pdf"
        )

        extracted_pages = []

        for page_number in range(len(pdf_document)):
            page = pdf_document.load_page(page_number)

            pixmap = page.get_pixmap(
                matrix=fitz.Matrix(2, 2),
                alpha=False
            )

            image = Image.open(
                BytesIO(pixmap.tobytes("png"))
            )

            page_text = pytesseract.image_to_string(
                image,
                lang="eng"
            )

            if page_text.strip():
                extracted_pages.append(page_text.strip())

        return "\n\n".join(extracted_pages).strip()

    except Exception as error:
        print(f"OCR extraction error: {error}")
        return ""

    finally:
        if pdf_document is not None:
            pdf_document.close()