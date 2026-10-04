import google.generativeai as genai
from app.config import settings
import os

api_key = settings.gemini_api_key
genai.configure(api_key=api_key)

print("Available models:")
for m in genai.list_models():
    if 'generateContent' in m.supported_generation_methods:
        print(m.name)
