# Resume Genie

AI-powered resume toolkit built with Streamlit and Grok-4 (xAI). Upload your resume PDF and get instant feedback, scoring, cover letters, and career coaching — all in one dashboard.

![Python](https://img.shields.io/badge/Python-3.12+-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.56+-red)
![LLM](https://img.shields.io/badge/LLM-Grok--4%20(xAI)-purple)

## Features

### Cover Letter Generator
Upload your resume and paste a job description to generate a tailored, professional cover letter (300–450 words). Supports real-time streaming output and markdown download.

### Resume-JD Matcher
Score how well your resume matches a specific job description. Returns keyword analysis, ATS compatibility score, readability score, skill gap analysis, and actionable improvement suggestions.

### Resume Checker
Standalone resume evaluator — no job description needed. Scores your resume on clarity, format, ATS-friendliness, and skills. Provides strengths, weaknesses, and recommended next career steps.

### Career Coach Chat
Interactive chatbot powered by your resume context. Ask about career guidance, interview prep, job search strategy, or skill gaps. Maintains full conversation history within the session.

## Quick Start

### Prerequisites

- Python 3.12+
- An [xAI API key](https://console.x.ai/) with Grok-4 access

### Setup

```bash
# Clone the repo
git clone https://github.com/Sourav692/Resume-Genie.git
cd Resume-Genie

# Create virtual environment
uv venv --python 3.12
source .venv/bin/activate

# Install dependencies
uv pip install --native-tls -e ".[dev]"
```

### Configure API Key

Create a `.streamlit/secrets.toml` file:

```toml
XAI_API_KEY = "your-xai-api-key-here"
```

Or set it as an environment variable:

```bash
export XAI_API_KEY="your-xai-api-key-here"
```

### Run

```bash
streamlit run main_dashboard.py
```

The app will open at `http://localhost:8501`.

## Project Structure

```
├── main_dashboard.py          # Unified dashboard with all 4 tools
├── cover_letter_generator.py  # Standalone cover letter app
├── resume_scorer.py           # Standalone resume-JD matcher app
├── resume_checker.py          # Standalone resume evaluator app
├── ai_career_coach.py         # Standalone career coach chatbot
├── demo.py                    # Hello World demo app
├── requirements.txt           # Pip dependencies
├── pyproject.toml             # Project config (uv/pip)
├── logo.png                   # App logo
└── Deployment.txt             # Server deployment notes
```

## Tech Stack

- **Frontend**: Streamlit
- **LLM**: Grok-4 via xAI API
- **Orchestration**: LangChain (langchain_xai, langchain_core, langchain_community)
- **PDF Parsing**: PyPDFLoader
- **Embeddings**: sentence-transformers

## Deployment

For server deployment (e.g., on an EC2 instance):

```bash
# Install dependencies
pip install -r requirements.txt

# Run in background
nohup python3 -m streamlit run main_dashboard.py &
```

## License

MIT
