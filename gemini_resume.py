import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

# Load API key from .env
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Use Gemini 1.5 Flash model
model = genai.GenerativeModel(model_name="models/gemini-1.5-flash-latest")

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

        # Clean markdown formatting if Gemini wraps it
        if json_text.startswith("```json"):
            json_text = json_text.strip("```json").strip("```").strip()

        resume_data = json.loads(json_text)
        return resume_data

    except Exception as e:
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
