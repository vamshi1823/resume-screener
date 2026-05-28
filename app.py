import os

import pdfplumber
import streamlit as st

from screener import screen_resume

st.set_page_config(page_title="AI Resume Screener", page_icon="🤖", layout="wide")

# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙️ Configuration")
    if "GROQ_API_KEY" in st.secrets:
        os.environ["GROQ_API_KEY"] = st.secrets["GROQ_API_KEY"]
        st.success("✓ API key loaded")
    else:
        api_key = st.text_input("Groq API Key", type="password", placeholder="gsk_...")
        if api_key:
            os.environ["GROQ_API_KEY"] = api_key
            st.success("✓ API key set")
    api_key = st.text_input("Groq API Key", type="password", placeholder="gsk_...")
    if api_key:
        os.environ["GROQ_API_KEY"] = api_key
        st.success("✓ API key set")
    st.divider()
    st.markdown("### 📌 About")
    st.info(
        "This tool uses Llama 3 via Groq API to analyze how well "
        "a resume matches a job description. Get a match score, "
        "skill gap analysis, and improvement suggestions instantly."
    )
    st.divider()
    st.markdown("### 🔗 Project Links")
    st.markdown("[![GitHub](https://img.shields.io/badge/GitHub-View_Source-black?logo=github)](https://github.com/vamshi1823/resume-screener)")
    st.markdown("**Stack:** Python · Groq · Llama 3 · Streamlit")

# ── Header ───────────────────────────────────────────────────────────────────
st.title("🤖 AI-Powered Resume Screener")
st.caption("Upload your resume and paste a job description — get an instant match score and skill gap analysis powered by Llama 3")
st.markdown("---")

# ── Input ────────────────────────────────────────────────────────────────────
col1, col2 = st.columns(2)

with col1:
    st.subheader("📋 Job Description")
    jd = st.text_area(
        "Paste the job description here",
        height=350,
        placeholder="Paste the full job description including required skills, responsibilities, and qualifications..."
    )

with col2:
    st.subheader("📄 Your Resume")
    upload_option = st.radio("Choose input method", ["Upload PDF", "Paste Text"], horizontal=True)

    resume_text = ""

    if upload_option == "Upload PDF":
        uploaded_file = st.file_uploader("Upload your resume (PDF)", type=["pdf"])
        if uploaded_file:
            with pdfplumber.open(uploaded_file) as pdf:
                resume_text = "\n".join(page.extract_text() or "" for page in pdf.pages)
            st.success(f"✅ Resume loaded — {len(resume_text)} characters extracted")
            with st.expander("👁️ Preview extracted text"):
                st.text(resume_text[:1000] + "..." if len(resume_text) > 1000 else resume_text)
    else:
        resume_text = st.text_area(
            "Paste your resume text here",
            height=300,
            placeholder="Paste your resume content — skills, experience, projects, education..."
        )

st.markdown("---")

# ── Analyze Button ───────────────────────────────────────────────────────────
col_btn, col_space = st.columns([1, 3])
with col_btn:
    analyze = st.button("🔍 Analyze Match", use_container_width=True)

if analyze:
    if not api_key:
        st.error("❌ Please enter your Groq API key in the sidebar")
    elif not jd.strip():
        st.error("❌ Please paste a job description")
    elif not resume_text.strip():
        st.error("❌ Please upload a PDF or paste your resume text")
    else:
        with st.spinner("Analyzing with Llama 3... this takes a few seconds"):
            result = screen_resume(jd, resume_text)

        if "error" in result:
            st.error(f"❌ Error: {result['error']}")
        else:
            st.markdown("---")
            st.subheader("📊 Analysis Results")

            score = result.get("match_score", 0)
            verdict = result.get("verdict", "Unknown")

            if score >= 75:
                color = "🟢"
            elif score >= 50:
                color = "🟡"
            else:
                color = "🔴"

            m1, m2, m3 = st.columns(3)
            m1.metric("Match Score", f"{score} / 100")
            m2.metric("Verdict", f"{color} {verdict}")
            m3.metric("Matched Skills", len(result.get("matched_skills", [])))

            st.progress(score / 100)
            st.markdown("---")

            c1, c2 = st.columns(2)

            with c1:
                st.markdown("### ✅ Matched Skills")
                matched = result.get("matched_skills", [])
                if matched:
                    for skill in matched:
                        st.markdown(f"- {skill}")
                else:
                    st.info("No matched skills found")

            with c2:
                st.markdown("### ❌ Missing Skills")
                missing = result.get("missing_skills", [])
                if missing:
                    for skill in missing:
                        st.markdown(f"- {skill}")
                else:
                    st.success("No critical skills missing!")

            st.markdown("---")

            c3, c4 = st.columns(2)

            with c3:
                st.markdown("### 💪 Strong Points")
                for point in result.get("strong_points", []):
                    st.markdown(f"- {point}")

            with c4:
                st.markdown("### 💡 Improvement Suggestions")
                for suggestion in result.get("improvement_suggestions", []):
                    st.markdown(f"- {suggestion}")

            st.markdown("---")
            st.caption("Built by Vasam Vamshi · [GitHub](https://github.com/vamshi1823/resume-screener) · AI Resume Screener Portfolio Project")