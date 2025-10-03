import streamlit as st
import datetime, re, json
from typing import List, Optional
from streamlit_lottie import st_lottie
from free_api_client import ask_ai

def generate_questions(interview_type: str, topic: Optional[str] = None) -> List[str]:
    base = f"Generate exactly ten {interview_type.lower()} interview questions"
    if interview_type.lower() == "technical" and topic:
        base += f" focused on the topic: {topic}."
    else:
        base += "."
    prompt = f"""
You are an experienced interviewer.
{base}
Return them as a plain numbered list without answers.
Vary questions across requests.
"""
    messages = [
        {"role": "system", "content": "You are a professional interviewer."},
        {"role": "user", "content": prompt}
    ]
    q_text = ask_ai(messages, max_tokens=350, temperature=0.8).strip()
    return [re.sub(r"^\d+\.\s*", "", ln).strip()
            for ln in q_text.splitlines() if ln.strip()]

def generate_answer_key(questions: List[str]) -> List[str]:
    prompt = """
Provide concise, correct answers for the following interview questions. Return exactly a numbered list of answers, one line per answer, no explanations.
""".strip() + "\n\n" + "\n".join(f"{i+1}. {q}" for i, q in enumerate(questions))
    messages = [
        {"role": "system", "content": "You are a concise subject matter expert."},
        {"role": "user", "content": prompt}
    ]
    text = ask_ai(messages, max_tokens=800, temperature=0.3).strip()
    answers = [re.sub(r"^\d+\.\s*", "", ln).strip() for ln in text.splitlines() if ln.strip()]
    # Ensure list length matches
    if len(answers) < len(questions):
        answers += [""] * (len(questions) - len(answers))
    return answers[:len(questions)]

def score_answers(questions: List[str], user_answers: List[str], correct_answers: List[str]) -> dict:
    qa = "\n\n".join(
        f"Q{i+1}: {q}\nUser: {ua}\nCorrect: {ca}"
        for i, (q, ua, ca) in enumerate(zip(questions, user_answers, correct_answers))
    )
    prompt = f"""
You are grading interview answers. For each question, provide only a numeric score 0-10.
Consider depth, correctness, and clarity. If the user answer is empty, score 0.
Return strict JSON with a single key "scores" mapping to a list of integers. No extra text.

{qa}
"""
    messages = [
        {"role": "system", "content": "You are a strict grader returning only valid JSON."},
        {"role": "user", "content": prompt}
    ]
    raw = ask_ai(messages, max_tokens=300, temperature=0.0)
    try:
        data = json.loads(raw)
        scores = data.get("scores", [])
        if not isinstance(scores, list):
            raise ValueError("scores not a list")
    except Exception:
        # Fallback heuristic: 0 for empty, 5 otherwise
        scores = [0 if not (ua and ua.strip()) else 5 for ua in user_answers]
    total = sum(int(s) for s in scores[:len(questions)])
    return {"scores": scores[:len(questions)], "total": total, "max": 10*len(questions)}

def load_lottie(filepath: str):
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

lottie_json = load_lottie("animations/Animation - 1749286005992.json")      

def run():
    st.title("🎤 Mock Interview Prep")
    st.markdown(
        "Practice common interview questions, type your answers, and receive AI-powered feedback."
    )

    st.markdown("""
    <style>
    .container {display:flex;align-items:center;justify-content:center;gap:2rem;flex-wrap:wrap;margin-bottom:1.5rem;}
    .input-box {max-width:380px;flex:1 1 380px;}
    .lottie-box{max-width:260px;flex:1 1 260px;}
    .stButton>button{width:100%}
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="container">', unsafe_allow_html=True)

    with st.container():
        st.markdown('<div class="input-box">', unsafe_allow_html=True)
        interview_type = st.radio("Choose interview focus:", ["Technical", "Behavioral"], horizontal=True)
        topic = ""
        if interview_type == "Technical":
            topic = st.text_input("Enter a technical topic (e.g., Python OOP, SQL Joins, React Hooks)")
        if st.button("Generate Questions", type="primary"):
            st.session_state.questions = generate_questions(interview_type, topic)
            st.session_state.answer_key = generate_answer_key(st.session_state.questions)
            st.session_state.start_time = datetime.datetime.now()
            st.session_state.feedback = None
            st.session_state.scores = None
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="lottie-box">', unsafe_allow_html=True)
    st_lottie(lottie_json, height=220, key="interview_lottie")
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True) 

    if "questions" in st.session_state:
        st.subheader("📋 Your Questions")
        answers = []
        for i, q in enumerate(st.session_state.questions, 1):
            st.write(f"**{i}. {q}**")
            answers.append(st.text_area("Your answer:", key=f"ans_{i}", height=120))

        colA, colB = st.columns([1, 3])
        with colA:
            if st.button("Submit & Score"):
                result = score_answers(st.session_state.questions, answers, st.session_state.answer_key)
                st.session_state.scores = result
        with colB:
            if "start_time" in st.session_state:
                elapsed = datetime.datetime.now() - st.session_state.start_time
                st.info(f"⏱️ Time since questions generated: {elapsed.seconds//60} min {elapsed.seconds%60} s")

        if st.session_state.get("scores"):
            sc = st.session_state.scores
            st.markdown("### 🧮 Score")
            st.success(f"Total: {sc['total']} / {sc['max']}")

            with st.expander("Show Correct Answers"):
                for i, (q, a) in enumerate(zip(st.session_state.questions, st.session_state.answer_key), 1):
                    st.markdown(f"**Q{i}. {q}**\n\n✅ {a}")

if __name__ == "__main__":
    run()
