<![CDATA[<div align="center">

#  AI Resume Analyzer(NLP)

**Instantly analyze your resume against any job description using NLP & Google Gemini API KEY**

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-2.0+-000000?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com)
[![Gemini](https://img.shields.io/badge/Google_Gemini-API-4285F4?style=for-the-badge&logo=google&logoColor=white)](https://ai.google.dev)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)

<br>

*Get your ATS score, keyword gaps, semantic match, and 10 actionable improvement suggestions — all in seconds.*

---

</div>

## ✨ Features

| Feature | Description |
|---------|-------------|
| 📊 **ATS Score** | Keyword-based compatibility score (0–100) refined by AI context analysis |
| 🧠 **Semantic Match** | Measures how well your overall profile fits the role beyond just keywords |
| 🔑 **Keyword Analysis** | Shows matched & missing keywords between your resume and the job description |
| 💪 **Strengths Detection** | Highlights areas where your resume strongly aligns with the JD |
| 🚀 **10 Actionable Suggestions** | Specific, prioritized recommendations referencing your actual resume content |
| 📄 **Multi-Format Upload** | Supports PDF, DOCX, and TXT resume files (up to 5 MB) |
| 🌗 **Dark / Light Mode** | Premium UI with theme toggle and smooth animations |
| ⚡ **Smart Retry** | Automatic exponential backoff (3 retries) for API rate limits |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────┐
│                    Frontend (HTML/CSS/JS)            │
│  ┌──────────┐  ┌──────────┐  ┌───────────────────┐  │
│  │ Upload   │  │   JD     │  │  Results Dashboard │  │
│  │ Drop Zone│  │ Textarea │  │  (Scores, Tags,   │  │
│  └────┬─────┘  └────┬─────┘  │   Suggestions)    │  │
│       │              │        └───────────────────┘  │
└───────┼──────────────┼──────────────────────────────┘
        │              │
        ▼              ▼
┌─────────────────────────────────────────────────────┐
│               Flask Backend (app.py)                 │
│  ┌──────────────┐  ┌─────────────┐  ┌────────────┐  │
│  │ File Parser   │  │ NLP Engine  │  │ Gemini API │  │
│  │ (PDF/DOCX/TXT)│  │ (Keywords,  │  │ (Deep      │  │
│  │               │  │  TF-IDF,    │  │  Analysis)  │  │
│  │               │  │  Cosine Sim)│  │             │  │
│  └──────────────┘  └─────────────┘  └────────────┘  │
└─────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.10+**
- **Google Gemini API Key** — [Get one free here](https://aistudio.google.com/app/apikey)

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/chbaladharmaraju/airesumeanalyzer.git
cd ai-resume-analyzer

# 2. Create a virtual environment
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up your API key
cp .env.example .env
# Edit .env and add your Gemini API key
```

### Configuration

Create a `.env` file in the project root:

```env
GEMINI_API_KEY=your_gemini_api_key_here
```

### Run

```bash
python app.py
```

Open **http://localhost:5000** in your browser — that's it! 🎉

---

## 📂 Project Structure

```
ai-resume-analyzer/
├── app.py                 # Flask server + Gemini integration + retry logic
├── nlp_processor.py       # NLP engine (keyword extraction, TF-IDF, cosine similarity)
├── requirements.txt       # Python dependencies
├── .env.example           # Environment variable template
├── sample_resume.txt      # Sample resume for testing
└── static/
    ├── index.html         # Single-page frontend
    ├── styles.css         # Premium design system (dark/light themes)
    └── app.js             # Frontend logic (drag & drop, API calls, rendering)
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | Python, Flask, Flask-CORS |
| **AI** | Google Gemini 2.0 Flash |
| **NLP** | Custom engine — TF-IDF scoring, cosine similarity, keyword extraction, section detection |
| **File Parsing** | PyPDF2 (PDF), python-docx (DOCX), built-in (TXT) |
| **Frontend** | Vanilla HTML5, CSS3, JavaScript (ES6+) |
| **Design** | Inter font, CSS custom properties, glassmorphism, micro-animations |

---

## ⚙️ How It Works

1. **Upload & Parse** — Your resume (PDF/DOCX/TXT) is parsed into plain text server-side
2. **NLP Pre-Analysis** — Keywords are extracted from both resume and JD using TF-IDF-weighted scoring with a built-in tech keyword dictionary (200+ terms). Cosine similarity and keyword overlap are computed
3. **AI Deep Analysis** — The resume text, JD, and NLP metrics are sent to Google Gemini, which returns a refined ATS score, semantic match, strengths, and 10 specific improvement suggestions
4. **Smart Retry** — If the API returns a 429 rate-limit error, the backend retries up to 3 times with exponential backoff (1s → 2s → 4s) before reporting failure
5. **Results Dashboard** — Scores animate in with ring charts, keywords are color-coded, and suggestions are collapsible with priority badges

---

## 🎨 UI Preview

| Dark Mode | Light Mode |
|-----------|------------|
| Premium dark theme with purple accent gradients | Clean light theme with soft shadows |

> Run the app locally to experience the full interactive UI with animations!

---

## 🔒 Privacy & Security

- ✅ **No data stored** — Resumes and job descriptions are processed in memory and never saved to disk or database
- ✅ **No tracking** — Zero analytics, cookies, or third-party scripts
- ✅ **API key stays local** — Your Gemini key is read from `.env` and never exposed to the frontend

---

## 📝 API Reference

### `POST /api/analyze`

| Parameter | Type | Description |
|-----------|------|-------------|
| `resume` | File | Resume file (PDF, DOCX, or TXT, max 5 MB) |
| `job_description` | String | Full job description text |

**Success Response (200):**

```json
{
  "ats_score": 72,
  "semantic_match": 68,
  "resume_summary": "...",
  "jd_summary": "...",
  "matched_keywords": ["python", "flask", "api"],
  "missing_keywords": ["kubernetes", "docker"],
  "strengths": ["Strong Python backend experience", "..."],
  "suggestions": [
    {
      "title": "Add Docker to skills",
      "detail": "The JD mentions Docker 3 times...",
      "priority": "high"
    }
  ]
}
```

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the project
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

<div align="center">

**Created by [Bala Dharmaraju](https://github.com/chbaladharmaraju)**

⭐ Star this repo if you found it useful!

</div>
]]>
