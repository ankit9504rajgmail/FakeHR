import streamlit as st
import pandas as pd
import os
import zipfile
import re
from employee_generator import generate_employee_data, PREDEFINED_FIELDS
from gemini_resume import generate_resume_with_gemini
from generate_pdf import save_resume_as_pdf
from database import (init_db, register_user, get_user, save_feedback,
                      get_all_feedback, save_generation_history, get_user_history)
from auth.hashing import hash_password, check_password
from io import BytesIO
import os, sys
import base64
import json
from datetime import datetime


print("\U0001F4C2 Current working directory:", os.getcwd())
print("\U0001F4C1 Files in this directory:", os.listdir())
print("\U0001F9E0 Python path:", sys.path)

st.set_page_config(page_title="FakeHR", layout="wide")
init_db()

if "user" not in st.session_state:
    st.session_state.user = None

def generate_download_link(file_path, link_text="Download PDF"):
    with open(file_path, "rb") as f:
        data = f.read()
    b64 = base64.b64encode(data).decode()
    href = f'<a href="data:application/octet-stream;base64,{b64}" download="{os.path.basename(file_path)}">{link_text}</a>'
    return href

# Add a banner with custom height and full width

def display_banner_image(image_path, max_height="250px"):

    with open(image_path, "rb") as img_file:
        encoded = base64.b64encode(img_file.read()).decode()

    st.markdown(
        f"""
        <div style="background-color: black; padding: 10px; border-radius: 8px; text-align: center; margin-bottom: 20px;">
            <img src="data:image/png;base64,{encoded}" 
                 style="width: 100%; max-height: {max_height}; object-fit: contain;" 
                 alt="FakeHR Banner">
        </div>
        """,
        unsafe_allow_html=True
    )


# 👇 Call it in your app where you want the banner
display_banner_image("static/banner.png")



st.markdown("---")

def auth_section():
    st.markdown("##  Welcome to FakeHR")

    if st.session_state.get("screen_width", 1000) < 768:
        # Stack vertically for mobile
        st.markdown("## Welcome to FakeHR")
        col1 = st.container()
        col2 = st.container()
    else:
        col1, col2 = st.columns([1, 1], gap="large")


    with col1:
            st.markdown("""
        ###  What is FakeHR?

        **FakeHR** is an AI-powered platform for HR professionals, developers, and educators to:
        -  Generate **synthetic employee data** for testing or mock use
        -  Instantly create **realistic, professional one-page resumes**
        -  Validate and demo your HR tools without real data

        ###  Why Use It?
        -  Saves time — no need to manually enter dummy data
        -  Uses Google Gemini AI for resume generation
        -  Great for startups, job coaching, interview practice

        
        """)  
        



    with col2:
        st.markdown(" ### Try it out for free by logging in or creating an account")
        tab1, tab2 = st.tabs(["🔐 Login", "🆕 Create Account"])

        with tab1:
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")

            if st.button("Login"):
                user = get_user(username)
                if user and check_password(password, user[2]):
                    st.success("Logged in successfully.")
                    st.session_state.user = {"id": user[0], "username": user[1]}
                    st.rerun()
                else:
                    st.error("Invalid username or password.")

        with tab2:
            new_username = st.text_input("New Username")
            email = st.text_input("Email")
            new_password = st.text_input("New Password", type="password")
            if st.button("Create Account"):
                if register_user(new_username, new_password):
                    st.success("Account created. You can now login.")
                else:
                    st.error("Username already exists.")
        

    st.markdown("---")
    st.subheader("💬 What Users Are Saying")

    feedback = get_all_feedback()
    if not feedback:
        st.info("No reviews yet. Be the first to leave feedback after using the app!")
    else:
        for username, rating, comment, created_at in feedback:
            st.markdown(f"**👤 {username}** &nbsp;&nbsp;⭐ {rating}/5")
            st.markdown(f"💭 _{comment}_")
            st.caption(f"🕒 {created_at}")
            st.markdown("---")


def dashboard():
    st.sidebar.image("static/logo.png", width=150)
    st.sidebar.success(f"Logged in as {st.session_state.user['username']}")

    option = st.sidebar.radio("Go to", [
    "📊 Generate Data",
    "📄 Generate Resumes",
    "⭐ Rate Us",
    "🕒 History",
    "🚪 Logout"
])

    generate_clicked = False

    if option == "\U0001F4CA Generate Data":
        st.header("\U0001F4CA Fake Employee Data Generator")
        num_rows = st.number_input("How many rows of data do you want?", 1, 1000, 10)

        field_options = list(PREDEFINED_FIELDS.keys())
        selected_fields = st.multiselect("Select predefined fields:", field_options, default=field_options[:5])
        custom_input = st.text_input("Add custom fields (comma-separated):", key="custom_fields_input")
        custom_fields = custom_input.split(',') if custom_input else []

        if st.button("Generate Data"):
            generate_clicked = True
            data = generate_employee_data(num_rows, selected_fields, custom_fields)
            df = pd.DataFrame(data)
            st.session_state.generated_data = df
            st.session_state.data_generated = True

        if "generated_data" in st.session_state and st.session_state.generated_data is not None:
            df = st.session_state.generated_data
            st.dataframe(df)

            csv = df.to_csv(index=False).encode()
            json_data = df.to_json(orient="records").encode()
            xlsx = BytesIO()
            df.to_excel(xlsx, index=False, engine="openpyxl")
            xlsx.seek(0)

            st.download_button("⬇️ Download CSV", csv, "employee_data.csv")
            st.download_button("⬇️ Download JSON", json_data, "employee_data.json")
            st.download_button("⬇️ Download Excel", xlsx, "employee_data.xlsx")

            # Save CSV & Excel to disk for history
            os.makedirs("output/generated", exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

            csv_path = f"output/generated/data_{timestamp}.csv"
            with open(csv_path, "wb") as f:
                f.write(csv)

            excel_path = f"output/generated/data_{timestamp}.xlsx"
            with open(excel_path, "wb") as f:
                f.write(xlsx.getbuffer())

            # Save generation history
            history_details = {
                "rows_generated": num_rows,
                "fields": selected_fields + custom_fields,
                "csv_path": csv_path,
                "xlsx_path": excel_path
            }

            save_generation_history(
                st.session_state.user["username"],
                "Fake Data",
                json.dumps(history_details)
            )

    elif option == "\U0001F4C4 Generate Resumes":
        st.header("\U0001F4C4 Resume Generator")
        st.markdown("---")
        resume_generator_ui()
        


    elif option == "\u2b50 Rate Us":
        st.header("\u2b50 Share Your Feedback")
        rating = st.slider("Rate your experience (1 to 5 stars):", 1, 5)
        comment = st.text_area("Leave a comment:")

        if st.button("Submit Feedback"):
            save_feedback(st.session_state.user['id'], rating, comment)
            st.success("Thanks for your feedback!")

    elif option == "🕒 History":
        history_tab(st.session_state.user['username'])
    
    elif option == "Logout":
        st.session_state.pop("user", None)
        st.success("✅ Logged out successfully!")
        st.rerun()


    st.markdown("---")
    st.subheader("\U0001F4E3 What Users Are Saying")
    for username, rating, comment, created_at in get_all_feedback():
        st.markdown(f"**{username}** \u2b50 {rating}/5")
        st.markdown(f"_{comment}_ ({created_at})")
        st.markdown("---")




def history_tab(username):
    st.header("📜 Your Generation History")

    history = get_user_history(username)

    if not history:
        st.info("No history found yet. Start generating data or resumes.")
        return

    # Sort by timestamp (latest first)
    history = sorted(history, key=lambda x: x[2], reverse=True)

    for idx, (data_type, details, timestamp) in enumerate(history, 1):
        icon = "📄" if data_type.lower() == "resume" else "📊"

        with st.expander(f"{icon} {idx}. {data_type} — {timestamp}"):
            st.markdown(f"**🕒 Timestamp:** {timestamp}")
            
            try:
                parsed = json.loads(details)

                if data_type.lower() == "fake data":
                    st.markdown(f"**🧾 Rows Generated:** {parsed.get('rows_generated', 'N/A')}")
                    st.markdown(f"**📌 Fields:** {', '.join(parsed.get('fields', []))}")
                elif data_type.lower() == "resume":
                    st.markdown(f"**📄 Total Resumes:** {parsed.get('count', 'N/A')}")
                    st.markdown(f"**👥 Names:** {', '.join(parsed.get('names', []))}")

                for label, path in parsed.items():
                    if isinstance(path, str) and os.path.exists(path):
                        ext = os.path.splitext(path)[1].lower()
                        if ext in [".csv", ".xlsx", ".zip"]:
                            with open(path, "rb") as f:
                                st.download_button(
                                    label=f"⬇️ Download {ext.upper()[1:]}",
                                    data=f.read(),
                                    file_name=os.path.basename(path),
                                    mime="application/zip" if ext == ".zip"
                                         else "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" if ext == ".xlsx"
                                         else "text/csv",
                                    key=f"{idx}_{label}"
                                )

            except json.JSONDecodeError:
                st.warning("⚠️ Could not parse saved details. Showing raw content:")
                st.markdown(details)



def resume_generator_ui():    
    st.subheader("📿 Bulk Resume Generator")

    if "data_generated" not in st.session_state or not st.session_state.data_generated:
        st.warning("⚠️ Please generate employee data first in the 'Generate Data' section.")
        return

    df = st.session_state.generated_data.copy()
    df.columns = [col.strip().lower() for col in df.columns]

    if "name" not in df.columns:
        st.error("❌ 'name' column is required to generate resumes.")
        return

    resume_fields = [col for col in df.columns if col != "resume"]

    default_resume_fields = ["name"]
    for field in ["job_title", "skills", "experience"]:
        if field in df.columns:
            default_resume_fields.append(field)

    optional_fields = [
        "education", "location", "email", "phone", 
        "linkedin", "github", "certifications"
    ]
    available_optional_fields = [f for f in optional_fields if f in df.columns and f not in default_resume_fields]

    # Hidden field selection (not shown to user)
    selected_fields = default_resume_fields + available_optional_fields

    if "name" not in selected_fields:
        st.warning("⚠️ 'name' must be included to generate resumes.")
        return

    resume_dir = "output/resumes"
    os.makedirs(resume_dir, exist_ok=True)
    resume_files = []

    st.markdown("### 👁️ Resume Previews")

    for index, row in df.iterrows():
        employee_data = row.to_dict()
        if not employee_data.get("name"):
            continue

        # Create prompt fields for Gemini
        prompt_fields = {}
        for key in selected_fields:
            display_key = "Job Title" if key == "job_title" else key
            prompt_fields[display_key] = employee_data.get(key, "")

        # Fallback to 'job_profiles' if 'job_title' is missing
        if "Job Title" not in prompt_fields or not prompt_fields["Job Title"]:
            if "job_profiles" in df.columns:
                prompt_fields["Job Title"] = employee_data.get("job_profiles", "")

        # Generate realistic resume data (JSON)
        with st.spinner(f"⏳ Generating resume for {employee_data['name']}..."):
            st.write("🚀 Sending request to Gemini API...")
            try:
                resume_data = generate_resume_with_gemini(prompt_fields)
                st.write("✅ Gemini API response received")

                contact = " | ".join(filter(None, [
                    employee_data.get("email", ""),
                    employee_data.get("phone", ""),
                    employee_data.get("linkedin", "")
                ]))

                pdf_path = save_resume_as_pdf(employee_data["name"], {
                    **resume_data,
                    "title": prompt_fields.get("Job Title", ""),
                    "contact": contact
                })

            except Exception as e:
                st.error(f"❌ Error generating resume for {employee_data['name']}: {e}")
                df.at[index, "resume"] = "❌ Failed"
                continue


        # Add preview section
        with st.expander(f"📄 Preview: {employee_data['name']}"):
            st.markdown(f"**Summary**: {resume_data.get('summary', '')}")
            st.markdown("**Experience:**")
            for exp in resume_data.get("experience", []):
                st.markdown(f"- {exp}")
            st.markdown("**Skills:**")
            st.markdown(", ".join(resume_data.get("skills", [])))
            if resume_data.get("projects"):
                st.markdown("**Projects:**")
                for proj in resume_data.get("projects", []):
                    st.markdown(f"- {proj}")
            if resume_data.get("awards"):
                st.markdown("**Awards:**")
                for award in resume_data.get("awards", []):
                    st.markdown(f"- {award}")

            # Add download button for individual resume
            if pdf_path and os.path.exists(pdf_path):
                with open(pdf_path, "rb") as f:
                    pdf_bytes = f.read()
                download_label = f"📄 Download {employee_data['name']}'s Resume"
                st.download_button(
                    label=download_label,
                    data=pdf_bytes,
                    file_name=os.path.basename(pdf_path),
                    mime="application/pdf",
                    key=f"download_{index}"
                )
                df.at[index, "resume"] = os.path.basename(pdf_path)  # ✅ Just the filename

                resume_files.append(pdf_path)
            else:
                st.error(f"❌ PDF not found for {employee_data['name']}")
                df.at[index, "resume"] = "❌ Failed"

    if not resume_files:
        st.warning("⚠️ No valid resumes were generated. Make sure selected fields have valid data.")
        return

    st.success("✅ Resumes generated successfully!")
    st.markdown("### 📅 Downloadable Resume Table")
    st.dataframe(df)

    st.markdown("### ⬇️ Download All Data")

    # CSV / JSON / Excel exports
    csv = df.to_csv(index=False).encode('utf-8')
    json_data = df.to_json(orient="records").encode('utf-8')
    excel_io = BytesIO()
    df.to_excel(excel_io, index=False, sheet_name="Resumes")
    excel_io.seek(0)

    st.download_button("📄 Download CSV", data=csv, file_name="employees.csv", mime="text/csv")
    st.download_button("🦾 Download JSON", data=json_data, file_name="employees.json", mime="application/json")
    st.download_button("📈 Download Excel", data=excel_io, file_name="employees.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    # Zip all resumes
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as zipf:
        for file_path in resume_files:
            arcname = os.path.basename(file_path)
            zipf.write(file_path, arcname=arcname)
    zip_buffer.seek(0)

    # Save ZIP to disk
    os.makedirs("output/zips", exist_ok=True)
    zip_path = "output/zips/all_resumes.zip"
    with open(zip_path, "wb") as f:
        f.write(zip_buffer.getvalue())

    # Download button
    st.download_button("📦 Download All Resumes (ZIP)", data=zip_buffer, file_name="all_resumes.zip", mime="application/zip")

    # Save history with structured details
    names = df['name'].tolist()
    history_details = {
        "count": len(resume_files),
        "names": names,
        "zip_path": zip_path
    }

    save_generation_history(
        st.session_state.user['username'],
        "Resume",
        json.dumps(history_details)
    )

    st.session_state.generated_resume_data = df.copy()



if st.session_state.user:
    dashboard()
else:
    auth_section()
