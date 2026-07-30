from io import BytesIO
import html

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak
)


def generate_patient_pdf(patient_report):
    """
    Generate a downloadable PDF from a saved patient report.

    Args:
        patient_report (dict): Saved patient report information.

    Returns:
        bytes: Generated PDF file data.
    """

    pdf_buffer = BytesIO()

    try:
        document = SimpleDocTemplate(
            pdf_buffer,
            pagesize=A4,
            rightMargin=40,
            leftMargin=40,
            topMargin=40,
            bottomMargin=40
        )

        styles = getSampleStyleSheet()

        title_style = ParagraphStyle(
            name="TitleStyle",
            parent=styles["Title"],
            alignment=TA_CENTER,
            fontSize=20,
            leading=24,
            spaceAfter=20,
            textColor=colors.darkblue
        )

        heading_style = ParagraphStyle(
            name="HeadingStyle",
            parent=styles["Heading2"],
            fontSize=14,
            leading=18,
            spaceBefore=12,
            spaceAfter=8,
            textColor=colors.darkblue
        )

        normal_style = ParagraphStyle(
            name="NormalStyle",
            parent=styles["BodyText"],
            fontSize=10,
            leading=15,
            spaceAfter=8
        )

        content = []

        # Main title
        content.append(
            Paragraph(
                "MedIntel AI Medical Report",
                title_style
            )
        )

        content.append(
            Paragraph(
                "AI-Powered Medical Report Analyzer",
                styles["Heading3"]
            )
        )

        content.append(Spacer(1, 12))

        # Safely read patient values
        patient_name = html.escape(
            str(patient_report.get("patient_name", ""))
        )

        age = html.escape(
            str(patient_report.get("age", ""))
        )

        gender = html.escape(
            str(patient_report.get("gender", ""))
        )

        phone = html.escape(
            str(patient_report.get("phone", ""))
        )

        report_type = html.escape(
            str(patient_report.get("report_type", ""))
        )

        report_date = html.escape(
            str(patient_report.get("report_date", ""))
        )

        patient_data = [
            ["Patient Name", patient_name],
            ["Age", age],
            ["Gender", gender],
            ["Phone", phone],
            ["Report Type", report_type],
            ["Report Date", report_date]
        ]

        patient_table = Table(
            patient_data,
            colWidths=[130, 350],
            repeatRows=1
        )

        patient_table.setStyle(
            TableStyle(
                [
                    (
                        "BACKGROUND",
                        (0, 0),
                        (0, -1),
                        colors.lightgrey
                    ),
                    (
                        "TEXTCOLOR",
                        (0, 0),
                        (0, -1),
                        colors.black
                    ),
                    (
                        "FONTNAME",
                        (0, 0),
                        (0, -1),
                        "Helvetica-Bold"
                    ),
                    (
                        "FONTNAME",
                        (1, 0),
                        (1, -1),
                        "Helvetica"
                    ),
                    (
                        "GRID",
                        (0, 0),
                        (-1, -1),
                        0.5,
                        colors.grey
                    ),
                    (
                        "VALIGN",
                        (0, 0),
                        (-1, -1),
                        "TOP"
                    ),
                    (
                        "LEFTPADDING",
                        (0, 0),
                        (-1, -1),
                        8
                    ),
                    (
                        "RIGHTPADDING",
                        (0, 0),
                        (-1, -1),
                        8
                    ),
                    (
                        "TOPPADDING",
                        (0, 0),
                        (-1, -1),
                        8
                    ),
                    (
                        "BOTTOMPADDING",
                        (0, 0),
                        (-1, -1),
                        8
                    )
                ]
            )
        )

        content.append(
            Paragraph(
                "Patient Information",
                heading_style
            )
        )

        content.append(patient_table)
        content.append(Spacer(1, 16))

        # Extracted medical report
        content.append(
            Paragraph(
                "Extracted Medical Report",
                heading_style
            )
        )

        extracted_text = patient_report.get(
            "extracted_text",
            "No extracted report text available."
        )

        if not extracted_text:
            extracted_text = "No extracted report text available."

        extracted_text = html.escape(
            str(extracted_text)
        ).replace("\n", "<br/>")

        content.append(
            Paragraph(
                extracted_text,
                normal_style
            )
        )

        content.append(PageBreak())

        # AI medical analysis
        content.append(
            Paragraph(
                "AI Medical Analysis",
                heading_style
            )
        )

        ai_analysis = patient_report.get(
            "ai_analysis",
            "No AI analysis available."
        )

        if not ai_analysis:
            ai_analysis = "No AI analysis available."

        ai_analysis = html.escape(
            str(ai_analysis)
        ).replace("\n", "<br/>")

        content.append(
            Paragraph(
                ai_analysis,
                normal_style
            )
        )

        content.append(Spacer(1, 20))

        content.append(
            Paragraph(
                "Disclaimer: This AI-generated report is for informational "
                "purposes only. It is not a confirmed medical diagnosis. "
                "Please consult a qualified medical professional.",
                styles["Italic"]
            )
        )

        document.build(content)

        return pdf_buffer.getvalue()

    except Exception as error:
        print(f"PDF generation error: {error}")
        raise

    finally:
        pdf_buffer.close()