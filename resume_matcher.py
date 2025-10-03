import streamlit as st
import pandas as pd
import re
import matplotlib.pyplot as plt
import json
from streamlit_lottie import st_lottie
from PyPDF2 import PdfReader
import io

# Load Lottie animation
def load_lottiefile(filepath: str):
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

lottie_resume = load_lottiefile("animations/Animation - 1749283614215.json")

@st.cache_data
def load_data():
    try:
        df = pd.read_csv('job_skills.csv')
        # Normalize columns
        expected_cols = {"category", "job_title", "skills"}
        missing = expected_cols - set(df.columns.str.lower())
        if missing:
            raise ValueError(f"job_skills.csv is missing columns: {missing}")
        # Ensure consistent casing
        df = df.rename(columns={c: c.lower() for c in df.columns})
        return df
    except Exception as e:
        st.error(f"Could not load job_skills.csv: {e}")
        return pd.DataFrame(columns=["category","job_title","skills"])

# Extract full text from PDF using PyPDF2 (free alternative)
def analyze_resume_pdf(pdf_bytes: bytes) -> str:
    reader = PdfReader(io.BytesIO(pdf_bytes))
    full_text = []
    for page in reader.pages:
        text = page.extract_text() or ""
        full_text.append(text)
    return " ".join(full_text).lower()

# Main app logic
def run():
    st.title("📄 Resume Skill Matcher")
    st.subheader("For students and working professionals")
    st.markdown("Upload your resume and see how well it aligns with the skills required for your desired job roles.")

    col1, col2 = st.columns([3, 2])
    with col2:
        st_lottie(lottie_resume, height=250, key="resume")

    with col1:
        df_jobs = load_data()

        # Choose category and role
        categories = sorted(df_jobs['category'].dropna().unique().tolist())
        category = st.radio("🎯 Category:", options=categories, horizontal=True if len(categories)<=4 else False)
        filtered_jobs = df_jobs[df_jobs['category'] == category]

        # Select job
        job_titles = sorted(filtered_jobs['job_title'].dropna().unique().tolist())
        selected_job_title = st.selectbox("💼 Select a Job Title:", job_titles)

        # Get the corresponding skills
        selected_row = filtered_jobs[filtered_jobs['job_title'] == selected_job_title].iloc[0]
        job_skills_str = selected_row.get('skills', '')
        skills_list = [skill.strip().lower() for skill in str(job_skills_str).split(',') if skill.strip()]

        st.markdown(f"### ✅ Skills Required for **{selected_job_title}**")
        st.write(", ".join(skills_list) if skills_list else "No skills listed for this role.")

        # Resume upload
        uploaded_file = st.file_uploader("📎 Upload your Resume (PDF only)", type=["pdf"])
        if uploaded_file:
            try:
                pdf_bytes = uploaded_file.read()
                resume_text = analyze_resume_pdf(pdf_bytes)

                with st.expander("🔍 Preview Extracted Resume Text (First 3000 characters)"):
                    st.text(resume_text[:3000] + ("..." if len(resume_text) > 3000 else ""))

                # Match skills
                matched = [skill for skill in skills_list if re.search(rf"\b{re.escape(skill)}\b", resume_text)]
                missing = [skill for skill in skills_list if skill not in matched]
                match_pct = round(100.0 * len(matched) / max(1, len(skills_list)), 1)

                st.metric(label="Match %", value=f"{match_pct}%", help="Percent of required skills found in resume")

                st.success(f"✅ Matched Skills ({len(matched)}):")
                st.markdown(", ".join(matched) if matched else "None")

                st.error(f"📌 Skills to Improve ({len(missing)}):")
                st.markdown(", ".join(missing) if missing else "None")

                # Pie chart
                def show_skill_gap_chart(matched, missing):
                    labels = ['Matched Skills', 'Missing Skills']
                    sizes = [len(matched), len(missing)]
                    colors = ['#4CAF50', '#FF5722']

                    fig, ax = plt.subplots()
                    wedges, _, autotexts = ax.pie(
                        sizes,
                        labels=labels,
                        autopct='%1.1f%%',
                        startangle=90,
                        colors=colors,
                        textprops={'color': "white"}
                    )
                    ax.axis('equal')
                    plt.setp(autotexts, size=12, weight="bold")
                    st.pyplot(fig)

                show_skill_gap_chart(matched, missing)

            except Exception as e:
                st.error(f"❌ Failed to analyze resume. Error: {e}")


