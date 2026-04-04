# main.py - Resume AI Toolkit (Grok-4 Powered)
import streamlit as st
import os
import tempfile
from langchain_xai import ChatXAI
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.prompts import PromptTemplate
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

# ───────────────────────────────────────────────
# CONFIG (shared across all tools)
# ───────────────────────────────────────────────
st.set_page_config(
    page_title="Resume Genie", 
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

from PIL import Image

logo = Image.open("logo.png")
st.sidebar.image(logo,width=80)

st.sidebar.markdown("**Resume Genie**")

XAI_API_KEY = "API KEY"
os.environ["XAI_API_KEY"] = XAI_API_KEY
XAI_API_KEY = os.getenv("XAI_API_KEY") or st.secrets.get("XAI_API_KEY", "")
if not XAI_API_KEY:
    st.error("❌ **XAI_API_KEY missing**. Add to `.streamlit/secrets.toml` or env vars.")
    st.stop()

@st.cache_resource(show_spinner="🔄 Initializing Grok-4...")
def get_llm():
    return ChatXAI(model="grok-4", api_key=XAI_API_KEY, temperature=0.2, max_tokens=2000)

llm = get_llm()

# ───────────────────────────────────────────────
# SHARED PDF LOADER
# ───────────────────────────────────────────────
@st.cache_data
def extract_resume_text(uploaded_file):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(uploaded_file.getvalue())
        tmp_path = tmp.name
    try:
        loader = PyPDFLoader(tmp_path)
        docs = loader.load()
        text = "\n\n".join(doc.page_content for doc in docs)
        return text
    finally:
        os.unlink(tmp_path)

# ───────────────────────────────────────────────
# PROMPTS (pre-defined for each tool)
# ───────────────────────────────────────────────
COVER_LETTER_PROMPT = PromptTemplate.from_template("""
Write a professional cover letter (300–450 words) for this job. Match resume to JD exactly. Standard format.
Job Description: {job_description}
Resume: {resume_text}
Do not invent facts.
""")

RESUME_SCORER_PROMPT = """You are an expert resume scorer. Analyze match to JD. EXACT structure:
**Score**: X/100
**Overall Match**: X%
Keywords matched: • ...
Missing keywords: • ...
Readability Score: X/100
ATS Compatibility Score: X/100
2-liner summary: ...
Skill gap analysis: • ...
Overall improvement suggestions: • ...
Industry specific feedback: • ...
Job: {job_description}
Resume: {context}
Be honest, use rubrics."""

RESUME_CHECKER_PROMPT = PromptTemplate.from_template("""
Score resume standalone (clarity, format, ATS, skills): EXACT structure:
1. **Score**: X/100
2. **Strengths**: • ...
3. **Weaknesses**: • ...
4. **Skills Mentioned**: • ...
5. **Recommended Skills**: • ...
6. **Next Career Steps**: • ...
Resume: {context}
""")

# ───────────────────────────────────────────────
# MAIN UI
# ───────────────────────────────────────────────
st.title("🚀 Resume Genie")
st.markdown("""
**Powered by Grok-4 (xAI)** • Your all-in-one solution for job applications  
**AI Tools** to craft winning resumes, cover letters & career strategies 💼✨
""")

# ─── LEFT SIDEBAR: Tool Selector ───
st.sidebar.title("🛠️ Select Tool")
tool = st.sidebar.radio("Choose a service:", [
    "✉️ Cover Letter Generator",
    "📊 Resume-JD Matcher", 
    "🔍 Resume Checker",
    "💬 Career Coach Chat"
], index=0, horizontal=False)

# Shared inputs (positioned based on tool)
if tool in ["✉️ Cover Letter Generator", "📊 Resume-JD Matcher"]:
    st.sidebar.subheader("📤 Inputs")
    job_desc = st.sidebar.text_area("Job Description", height=200, key="jd_shared")
    resume_file = st.sidebar.file_uploader("Resume PDF", type="pdf", key="resume_shared")

# ───────────────────────────────────────────────
# TOOL 1: COVER LETTER
# ───────────────────────────────────────────────
if tool == "✉️ Cover Letter Generator":
    st.header("✉️ AI Cover Letter Generator")
    col1, col2 = st.columns([1,1])
    
    with col1:
        st.subheader("📝 Job Description")
        job_description = st.text_area("Paste JD", value=job_desc or "", height=350, key="jd_cl")
    
    with col2:
        st.subheader("📄 Your Resume")
        uploaded_file = st.file_uploader("Upload PDF", type="pdf", key="cl_resume")
        if uploaded_file:
            if st.button("🔥 Generate Cover Letter", type="primary"):
                with st.spinner("Extracting → Generating..."):
                    resume_text = extract_resume_text(uploaded_file)
                    chain = COVER_LETTER_PROMPT | llm
                    full_response = ""
                    resp_container = st.empty()
                    for chunk in chain.stream({"job_description": job_description, "resume_text": resume_text}):
                        content = chunk.content if hasattr(chunk, "content") else str(chunk)
                        full_response += content
                        resp_container.markdown(full_response + "▌")
                    resp_container.markdown(full_response)
                    st.download_button("💾 Download .md", full_response, "cover_letter.md")

# ───────────────────────────────────────────────
# TOOL 2: RESUME SCORER/MATCHER
# ───────────────────────────────────────────────
elif tool == "📊 Resume-JD Matcher":
    st.header("📊 Resume vs Job Description Matcher")
    col1, col2 = st.columns([1,1])
    
    with col1:
        st.subheader("📋 Job Description")
        job_description = st.text_area("Paste full JD", value=job_desc or "", height=350, key="jd_scorer")
    
    with col2:
        st.subheader("📄 Resume")
        uploaded_file = st.file_uploader("Upload PDF", type="pdf", key="scorer_resume")
        if uploaded_file:
            st.success("✅ Resume loaded")
            if st.button("📈 Score Match", type="primary"):
                with st.spinner("Analyzing match... (30-60s)"):
                    context = extract_resume_text(uploaded_file)
                    prompt = RESUME_SCORER_PROMPT.format(job_description=job_description, context=context)
                    response = llm.invoke(prompt)
                    st.markdown("### 📊 **Analysis Result**")
                    st.markdown(response.content)

# ───────────────────────────────────────────────
# TOOL 3: RESUME CHECKER
# ───────────────────────────────────────────────
elif tool == "🔍 Resume Checker":
    st.header("🔍 Standalone Resume Evaluator")
    uploaded_file = st.file_uploader("Upload resume PDF", type="pdf", key="checker_resume")
    
    if uploaded_file and st.button("Evaluate Resume", type="primary"):
        with st.spinner("Evaluating..."):
            context = extract_resume_text(uploaded_file)
            chain = RESUME_CHECKER_PROMPT | llm
            response = chain.invoke({"context": context})
            st.markdown("### 📋 **Detailed Evaluation**")
            st.markdown(response.content)

# ───────────────────────────────────────────────
# TOOL 4: CAREER COACH CHAT
# ───────────────────────────────────────────────
elif tool == "💬 Career Coach Chat":
    st.header("💬 Career Coach Chatbot")
    
    # Resume upload (session-persisted)
    if "resume_context" not in st.session_state:
        st.session_state.resume_context = None
        st.session_state.chat_history = []
    
    uploaded_file = st.file_uploader("Upload resume first", type="pdf", key="chat_resume")
    if uploaded_file and st.session_state.resume_context is None:
        context = extract_resume_text(uploaded_file)
        st.session_state.resume_context = context
        st.rerun()
    
    if not st.session_state.resume_context:
        st.warning("👆 Upload your resume to start chatting!")
        st.stop()
    
    # Layout: Left=Resume | Right=Chat
    left_col, right_col = st.columns([1,1])
    
    with left_col:
        st.subheader("📄 Your Resume")
        with st.expander("View full text", expanded=True):
            st.text_area("", st.session_state.resume_context, height=500, disabled=True)
    
    with right_col:
        st.subheader("🤖 Career Coach")
        system_msg = SystemMessage(content=f"""You are a career coach. Use this resume: {st.session_state.resume_context}""")
        
        # Chat history
        for msg in st.session_state.chat_history:
            role = "user" if isinstance(msg, HumanMessage) else "assistant"
            with st.chat_message(role):
                st.markdown(msg.content)
        
        # Chat input
        if prompt := st.chat_input("Ask about career, resume, interviews..."):
            st.session_state.chat_history.append(HumanMessage(content=prompt))
            with st.chat_message("assistant"):
                messages = [system_msg] + st.session_state.chat_history
                resp_container = st.empty()
                full_resp = ""
                for chunk in llm.stream(messages):
                    full_resp += chunk.content
                    resp_container.markdown(full_resp + "▌")
                resp_container.markdown(full_resp)
            st.session_state.chat_history.append(AIMessage(content=full_resp))
            st.rerun()

# ───────────────────────────────────────────────
# FOOTER
# ───────────────────────────────────────────────
st.markdown("---")
col1, col2, col3 = st.columns(3)
with col1:
    st.caption("✅ **Ready**: All 4 tools live")
with col2:
    st.caption("🔑 **API**: Grok-4 (xAI)")
with col3:
    st.caption("📅 **Built**: Jan 2026 • Satyajit")

st.sidebar.markdown("---")
st.sidebar.caption("**Pro Tips**: Use sidebar to switch tools instantly ⚡")