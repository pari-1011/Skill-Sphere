import streamlit as st
import json
from streamlit_lottie import st_lottie
from PyPDF2 import PdfReader
from free_api_client import ask_ai

def parse_resume(uploaded_file):
    try:
        reader = PdfReader(uploaded_file)
        full_text = []
        for page in reader.pages:
            text = page.extract_text() or ""
            full_text.append(text)
        return " ".join(full_text)
    except Exception as e:
        raise RuntimeError(f"Failed to read PDF: {e}")

def analyze_resume_content(resume_text):
    prompt = f"""
You are a career guidance expert. Analyze the following resume content:

\"\"\"{resume_text}\"\"\"

Provide:
1. Key strengths based on skills and experience
2. Gaps or weaknesses to improve
3. A learning roadmap to address these gaps

Respond clearly in a structured format.
"""
    messages = [
        {"role": "system", "content": "You are a helpful and insightful career coach."},
        {"role": "user", "content": prompt}
    ]
    return ask_ai(messages, max_tokens=1000, temperature=0.7)

def load_lottiefile(filepath: str):
    with open(filepath, "r") as f:
        return json.load(f)

lottie_resume = load_lottiefile("animations/Animation - 1749285315567.json") 

def run():
    st.title("🛠️ Skill Builder via Resume")
    st.markdown("Upload your resume to receive personalized feedback on your strengths, weaknesses, and a learning roadmap.")

    st.markdown(
        """
        <style>
        .container {
            display: flex;
            justify-content: center;
            align-items: flex-start;
            gap: 3rem;
            margin-top: 20px;
            flex-wrap: wrap;
        }
        .input-area {
            max-width: 450px;
            flex: 1 1 450px;
        }
        .animation-area {
            max-width: 300px;
            flex: 1 1 300px;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.markdown('<div class="container">', unsafe_allow_html=True)

    st.markdown('<div class="input-area">', unsafe_allow_html=True)
    uploaded_file = st.file_uploader("📄 Upload Resume (PDF)", type=["pdf"])
    analyze_clicked = st.button("Analyze Resume")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="animation-area">', unsafe_allow_html=True)
    st_lottie(lottie_resume, height=280, key="resume_lottie")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    if uploaded_file and analyze_clicked:
        with st.spinner("Reading and analyzing your resume..."):
            try:
                resume_text = parse_resume(uploaded_file)
                analysis = analyze_resume_content(resume_text)

                st.markdown("### ✅ Career Analysis Result")
                st.markdown(analysis)

            except Exception as e:
                st.error(f"Something went wrong: {e}")

if __name__ == "__main__":
    run()
