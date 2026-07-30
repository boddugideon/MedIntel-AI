import fitz  # PyMuPDF

def extract_pdf_text(uploaded_file):
    text = ""

    try:
        # Open uploaded PDF
        pdf = fitz.open(
            stream=uploaded_file.read(),
            filetype="pdf"
        )

        # Read every page
        for page in pdf:
            text += page.get_text("text")

        pdf.close()

        return text

    except Exception as e:
        return f"Error reading PDF: {e}"