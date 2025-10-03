import streamlit as st
import json
from streamlit_lottie import st_lottie
from free_api_client import ask_ai

def load_lottiefile(filepath: str):
    with open(filepath, "r") as f:
        return json.load(f)

def run():
    st.markdown(
        """
        <style>
        .centered-container {
            max-width: 700px;
            margin-left: auto;
            margin-right: auto;
            text-align: center;
        }
        .stButton>button {
            width: 100%;
        }
        </style>
        """, unsafe_allow_html=True)

    with st.container():
        st.markdown('<div class="centered-container">', unsafe_allow_html=True)

        lottie_json = load_lottiefile("animations/Animation - 1749284783217.json")  

        st_lottie(lottie_json, height=150, key="course-animation")

        st.title("🎯 Course Recommendations")

        topics = st.text_input(
            "Enter one or more topics (comma separated, e.g. Flutter, Data Engineering):", 
            placeholder="e.g. Python, Cloud Computing"
        )

        if st.button("Get Recommendations") and topics.strip() != "":
            with st.spinner("Fetching course recommendations..."):
                prompt = f"""
                Suggest top 10 high-quality online courses for the following topics: {topics}.
                For each course, include:
                - Platform name (Coursera, Udemy, edX, etc.)
                - Course title as clickable Markdown link (format: [Course Title](url))
                - A brief reason why the course is recommended.
                Provide the list as bullet points in Markdown format.
                """

                try:
                    messages = [
                        {"role": "system", "content": "You are a helpful course recommendation assistant."},
                        {"role": "user", "content": prompt}
                    ]
                    recommendations = ask_ai(messages, max_tokens=800, temperature=1.0)
                    st.markdown("### 📚 Recommended Courses")
                    st.markdown(recommendations)

                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")

        st.markdown('</div>', unsafe_allow_html=True)
