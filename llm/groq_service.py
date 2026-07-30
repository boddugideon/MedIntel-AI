from groq import Groq
import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)


def analyze_report(report_text):
    prompt = f"""
    You are a medical AI assistant.

    Explain the following medical report in simple language.

    Medical Report:
    {report_text}
    """

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    return response.choices[0].message.content