import os
from google import genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

response = client.models.generate_content(
    model="gemini-2.0-flash",
    contents="Say Hello"
)

print(response.text)