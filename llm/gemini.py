import os
import streamlit as st
from dotenv import load_dotenv, find_dotenv
from google import genai

def analyze_report(report_text: str) -> str:
    # 1. Load environment variables dynamically when the function runs
    load_dotenv(find_dotenv(), override=True)

    # 2. Extract API Key (checks .env first, then Streamlit secrets)
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")

    if not api_key:
        try:
            api_key = st.secrets["GEMINI_API_KEY"]
        except Exception:
            pass

    if not api_key or api_key == "your_actual_gemini_api_key_here":
        raise ValueError(
            "❌ Invalid API key. Please check your .env file and ensure GEMINI_API_KEY contains a valid key."
        )

    # 3. Create client directly with the retrieved key
    client = genai.Client(api_key=api_key)

    # 4. Prompt
    prompt = f"""
You are an experienced medical AI assistant.

Analyze the following medical report.

Provide the output in this format:

## Summary

## Normal Values

## Abnormal Values

## Possible Diseases

## Lifestyle Recommendations

Medical Report:
{report_text}
"""

    # 5. Generate Response
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt
    )

    return response.text