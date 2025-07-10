import os
import json
import google.generativeai as genai
import streamlit as st
from faker import Faker
import random

# Load Gemini API key from Streamlit secrets
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

# Use Gemini 1.5 Flash model
model = genai.GenerativeModel(model_name="models/gemini-1.5-flash-latest")

# Faker for fallback
faker = Faker()

def generate_resume_with_gemini(fields):
    name = fields.get("name", "John Doe")
    job_title = fields.get("Job Title") or fields.get("job_title") or "General Professional"

    # Prompt for Gemini
    prompt = f"""
You are a professional resume writer.

Generate a clean, realistic, one-page resume based on the details below. If a specific job title is provided, tailor the resume accordingly. Fill all fields with real, professional content. Do not use placeholders or dummy values.

### Required JSON Fields:
- "summary": 2–3 sentence professional overview (written in third person).
- "experience": 4–6 bullet points of achievements and work impact.
- "education": 1-line highest degree with institution and year.
- "certifications": Short string (or empty if none).
- "skills": 5–8 relevant technical or soft skills.
- "languages": 2–3 languages with proficiency levels.
- "projects": 2–3 realistic project descriptions (1–2 lines each).
- "awards": 1–3 professional awards or recognitions.

### Candidate Details:
{json.dumps(fields, indent=2)}

### Output JSON Format:
{{
  "summary": "...",
  "experience": ["...", "..."],
  "education": "...",
  "certifications": "...",
  "skills": ["...", "..."],
  "languages": ["...", "..."],
  "projects": ["...", "..."],
  "awards": ["...", "..."]
}}

Only return the JSON object. Do not include any markdown or text outside the JSON.
"""

    try:
        response = model.generate_content(prompt)
        json_text = response.text.strip()

        # If Gemini wrapped it in a code block
        if json_text.startswith("```json"):
            json_text = json_text.strip("```json").strip("```").strip()

        if "429" in json_text or "quota" in json_text.lower():
            raise Exception("QuotaExceeded")

        resume_data = json.loads(json_text)
        return resume_data

    except Exception as e:
        if "QuotaExceeded" in str(e) or "quota" in str(e).lower():
            return generate_fallback_resume(name)
        return {
            "summary": f"Error generating resume: {str(e)}",
            "experience": [],
            "education": "",
            "certifications": "",
            "skills": [],
            "languages": [],
            "projects": [],
            "awards": []
        }

def generate_fallback_resume(name):
    return {
        "summary": f"{name} is a passionate and dedicated professional with strong expertise in {faker.job().lower()} and a proven track record of delivering results.",
        "experience": [
            f"{faker.job()} at {faker.company()} (2 years)",
            f"{faker.job()} at {faker.company()} (1.5 years)",
            f"Improved team efficiency by 25% at {faker.company()}",
            f"Led {faker.bs()} project saving $50K annually",
        ],
        "education": f"{random.choice(['B.Sc', 'B.Tech', 'M.Sc', 'MBA', 'Ph.D'])} from {faker.company()} University, {faker.year()}",
        "certifications": f"{faker.bs().title()} Certificate",
        "skills": [faker.word().capitalize() for _ in range(6)],
        "languages": [f"{faker.language_name()} - Fluent", "English - Native"],
        "projects": [
            f"{faker.catch_phrase()}: {faker.text(max_nb_chars=100)}",
            f"{faker.catch_phrase()}: {faker.text(max_nb_chars=100)}"
        ],
        "awards": [faker.sentence(nb_words=5) for _ in range(2)]
    }
