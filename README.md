# Resume Genie

> An AI-powered career suite that turns your resume PDF into actionable insights -- instant scoring, tailored cover letters, ATS optimization, and interactive career coaching, all from one Streamlit dashboard.

 

<!-- image: width=800 -->
![Resume Genie — An AI-Powered Career Suite](assets/image.png)

 

 

![Python](https://img.shields.io/badge/Python-3.12+-3776AB?logo=python&logoColor=white)

 

![Streamlit](https://img.shields.io/badge/Streamlit-1.45+-FF4B4B?logo=streamlit&logoColor=white)

 

![LLM](https://img.shields.io/badge/LLM-Llama--3.3--70B-7C3AED)

 

![Groq](https://img.shields.io/badge/Provider-Groq-F55036?logo=data:image/svg+xml;base64,&logoColor=white)

 

![LangChain](https://img.shields.io/badge/LangChain-Framework-1C3C3C?logo=langchain&logoColor=white)

 

![License](https://img.shields.io/badge/License-MIT-22C55E)

 

---

## Features

| Tool | What it does |
| --- | --- |
| **Cover Letter Generator** | Upload resume + paste JD to generate a tailored 300-450 word cover letter with streaming output and markdown download |
| **Resume-JD Matcher** | Score your resume against a job description -- keyword analysis, ATS compatibility, readability, skill gaps, and improvement suggestions |
| **Resume Checker** | Standalone resume evaluation (no JD needed) -- scores clarity, format, ATS-friendliness, skills inventory, and next career steps |
| **Career Coach Chat** | Interactive chatbot grounded in your resume context -- career guidance, interview prep, job search strategy with full conversation history |

All four tools share the same LLM backend and PDF extraction pipeline. Each can run standalone or from the unified dashboard.

## Architecture

```
                         ┌─────────────────────────────────┐
                         │      Streamlit Dashboard        │
                         │     (main_dashboard.py)         │
                         │                                 │
                         │  ┌───────────┐  ┌───────────┐  │
  Upload PDF ──────────► │  │ Cover     │  │ Resume-JD │  │
                         │  │ Letter    │  │ Matcher   │  │
                         │  └───────────┘  └───────────┘  │
  Paste Job ──────────►  │  ┌───────────┐  ┌───────────┐  │
  Description            │  │ Resume    │  │ Career    │  │
                         │  │ Checker   │  │ Coach     │  │
                         │  └───────────┘  └───────────┘  │
                         └────────┬───────────┬───────────┘
                                  │           │
                         ┌────────▼──┐  ┌─────▼──────────┐
                         │PyPDFLoader│  │   ChatGroq     │
                         │ PDF→Text  │  │ Llama 3.3 70B  │
                         └───────────┘  └────────────────┘
```

## Quick Start

### Prerequisites

- Python 3.12+
- A free [Groq API key](https://console.groq.com/)

### Setup

```bash
# Clone
git clone https://github.com/Sourav692/Resume-Genie.git
cd Resume-Genie

# Virtual environment (using uv)
uv venv --python 3.12
source .venv/bin/activate

# Install
uv pip install -e ".[dev]"
```

Alternative: using pip

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Configure

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your-groq-api-key-here
```

### Run

```bash
# Unified dashboard (all 4 tools)
streamlit run scripts/main_dashboard.py
```

Opens at `http://localhost:8501`. Use the sidebar to switch between tools.

**Run individual tools:**

```bash
streamlit run scripts/cover_letter_generator.py
streamlit run scripts/resume_scorer.py
streamlit run scripts/resume_checker.py
streamlit run scripts/ai_career_coach.py
```

## Project Structure

```
Resume-Genie/
├── scripts/
│   ├── main_dashboard.py          # Unified dashboard with all 4 tools
│   ├── cover_letter_generator.py  # Standalone cover letter generator
│   ├── resume_scorer.py           # Standalone resume-JD matcher
│   ├── resume_checker.py          # Standalone resume evaluator
│   └── ai_career_coach.py         # Standalone career coach chatbot
├── notebooks/
│   ├── AI_Career_Coach.ipynb      # Career coach notebook prototype
│   ├── Cover_Letter_Generator.ipynb
│   ├── Resume_Scorer.ipynb
│   └── Resume_Checker.ipynb
├── assets/
│   ├── image.png                  # Project banner
│   ├── logo.png                   # App sidebar logo
│   ├── architecture.png           # Architecture diagram
│   └── architecture.excalidraw    # Editable architecture source
├── content/
│   └── Resume.pdf                 # Sample resume for testing
├── .env                           # API keys (git-ignored)
├── pyproject.toml                 # Project metadata and dependencies
├── requirements.txt               # Pip dependencies
├── Deployment.txt                 # Server deployment notes
└── uv.lock                        # Lockfile for reproducible installs
```

## Tech Stack

| Layer | Technology |
| --- | --- |
| **Frontend** | Streamlit |
| **LLM** | Llama 3.3 70B Versatile |
| **Inference** | Groq (ultra-low latency) |
| **Orchestration** | LangChain (`langchain_groq`, `langchain_core`, `langchain_community`) |
| **PDF Parsing** | PyPDFLoader via `langchain_community` |
| **Config** | python-dotenv |

## Deployment (EC2 / Remote Server)

```bash
# System setup (Ubuntu/Debian)
sudo apt update && sudo apt install python3-pip python3-venv -y

# Project setup
git clone https://github.com/Sourav692/Resume-Genie.git
cd Resume-Genie
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Run in background (survives SSH disconnect)
nohup python3 -m streamlit run scripts/main_dashboard.py &

# Monitor logs
tail -f nohup.out
```

## License

MIT