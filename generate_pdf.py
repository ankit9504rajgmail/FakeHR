import os
import re
from jinja2 import Environment, FileSystemLoader

# Use WeasyPrint by default
USE_WEASY = os.getenv("USE_WEASY", "1") == "1"

if USE_WEASY:
    from weasyprint import HTML  # ✅ Works on Streamlit Cloud
else:
    import pdfkit
    # Set this to your local wkhtmltopdf path
    WKHTMLTOPDF_PATH = r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe"
    pdfkit_config = pdfkit.configuration(wkhtmltopdf=WKHTMLTOPDF_PATH)

def sanitize_filename(name):
    """Clean the filename to avoid illegal characters and keep it short."""
    name = re.sub(r'[^\w\s-]', '', name)
    name = name.strip().replace(' ', '_')
    return name[:50]

def save_resume_as_pdf(name, resume_data, directory="output/resumes"):
    os.makedirs(directory, exist_ok=True)

    # Load Jinja2 HTML template
    env = Environment(loader=FileSystemLoader("templates"))
    template = env.get_template("resume_template.html")

    # Render HTML from template
    html_out = template.render(
        name=name,
        title=resume_data.get("title", ""),
        summary=resume_data.get("summary", ""),
        experience=resume_data.get("experience", []),
        education=resume_data.get("education", ""),
        certifications=resume_data.get("certifications", ""),
        skills=resume_data.get("skills", []),
        contact=resume_data.get("contact", ""),
        languages=resume_data.get("languages", []),
        projects=resume_data.get("projects", []),
        awards=resume_data.get("awards", [])
    )

    # Create safe file path
    safe_name = sanitize_filename(name)
    pdf_path = os.path.join(directory, f"{safe_name}_Resume.pdf")

    # Generate PDF with selected backend
    if USE_WEASY:
        HTML(string=html_out).write_pdf(pdf_path)
    else:
        pdfkit.from_string(html_out, pdf_path, configuration=pdfkit_config)

    return pdf_path
