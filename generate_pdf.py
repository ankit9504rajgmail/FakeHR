import os
import re
import pdfkit
from jinja2 import Environment, FileSystemLoader

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

    # Detect platform and set wkhtmltopdf path
    if os.name == 'nt':  # Windows
        wkhtmltopdf_path = r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe"
    else:  # Linux/Streamlit Cloud
        wkhtmltopdf_path = "/usr/bin/wkhtmltopdf"

    config = pdfkit.configuration(wkhtmltopdf=wkhtmltopdf_path)

    # Generate PDF using pdfkit
    pdfkit.from_string(html_out, pdf_path, configuration=config)

    return pdf_path
