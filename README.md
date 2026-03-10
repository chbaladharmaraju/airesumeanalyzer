

# 🧠 AI Resume Analyzer (NLP)

Analyze your resume against any job description using **Natural Language Processing and Google Gemini AI** to get an **ATS compatibility score, semantic match, keyword gaps, and improvement suggestions in seconds.**

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge\&logo=python\&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-Backend-000000?style=for-the-badge\&logo=flask)
![Gemini API ](https://img.shields.io/badge/Google-Gemini_AI-4285F4?style=for-the-badge\&logo=google)

---

# 🚀 Live Features

### 📊 ATS Compatibility Score

Evaluates resume compatibility with job descriptions using **NLP keyword weighting and AI refinement**.

### 🧠 Semantic Matching

Measures **contextual similarity** between resume and job description using **TF-IDF + Cosine Similarity**.

### 🔑 Keyword Gap Detection

Shows:

* ✔ Matched keywords
* ❌ Missing keywords

### 💪 Strength Identification

Highlights the **strongest parts of your resume** aligned with the role.

### 🚀 AI Improvement Suggestions

Provides **10 actionable improvements** based on Gemini AI analysis.

### 📄 Multi-Format Resume Support

Upload:

* PDF
* DOCX
* TXT

(max size: **5MB**)

### 🌗 Dark & Light Mode UI

Modern responsive UI with **smooth animations and theme switching**.

### ⚡ Smart Retry Logic

Handles **API rate limits automatically** using **exponential backoff retry strategy**.

---

# 🏗️ System Architecture

```
Frontend (HTML/CSS/JS)
│
├── Resume Upload (Drag & Drop)
├── Job Description Input
└── Results Dashboard

        ↓

Flask Backend (Python)
│
├── Resume Parser
│   ├── PyPDF2
│   ├── python-docx
│   └── TXT parser
│
├── NLP Engine
│   ├── Keyword Extraction
│   ├── TF-IDF scoring
│   └── Cosine Similarity
│
└── Gemini AI
    ├── Resume analysis
    ├── Semantic scoring
    └── Improvement suggestions
```

---

# ⚙️ Tech Stack

| Layer        | Technology                                    |
| ------------ | --------------------------------------------- |
| Backend      | Python, Flask, Flask-CORS                     |
| AI           | Google Gemini 2.0 Flash                       |
| NLP          | TF-IDF, Cosine Similarity, Keyword Extraction |
| File Parsing | PyPDF2, python-docx                           |
| Frontend     | HTML5, CSS3, JavaScript                       |
| UI Design    | Glassmorphism, Inter Font, Micro-Animations   |

---

# 📂 Project Structure

```
ai-resume-analyzer
│
├── app.py
├── nlp_processor.py
├── requirements.txt
├── .env.example
├── sample_resume.txt
│
└── static
    ├── index.html
    ├── styles.css
    └── app.js
```

---

# 🛠️ Installation

## 1️⃣ Clone Repository

```bash
git clone https://github.com/chbaladharmaraju/airesumeanalyzer.git

cd ai-resume-analyzer
```

---

## 2️⃣ Create Virtual Environment

```bash
python -m venv .venv
```

Activate:

### Windows

```
.venv\Scripts\activate
```

### Mac/Linux

```
source .venv/bin/activate
```

---

## 3️⃣ Install Dependencies

```
pip install -r requirements.txt
```

---

## 4️⃣ Add Gemini API Key

Create `.env`

```
GEMINI_API_KEY=your_api_key_here
```

Get key here

[https://aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)

---

## 5️⃣ Run Application

```
python app.py
```

Open:

```
http://localhost:5000
```

---

# ⚙️ How It Works

### Step 1 — Resume Upload

Resume is uploaded and parsed into **plain text**.

### Step 2 — NLP Processing

The NLP engine calculates:

* TF-IDF keyword weights
* Keyword overlap
* Cosine similarity

### Step 3 — AI Analysis

Gemini AI analyzes:

* Resume context
* Job description
* NLP metrics

It generates:

* ATS score
* Semantic match
* Resume strengths
* 10 improvement suggestions

### Step 4 — Smart Retry

If API rate limit occurs:

```
Retry 1 → 1 second
Retry 2 → 2 seconds
Retry 3 → 4 seconds
```

---

# 📊 Example API Response

`POST /api/analyze`

```
{
 "ats_score": 72,
 "semantic_match": 68,
 "matched_keywords": ["python","flask","api"],
 "missing_keywords": ["docker","kubernetes"],
 "strengths": [
   "Strong backend experience",
   "Good API development background"
 ],
 "suggestions": [
   {
     "title": "Add Docker Experience",
     "detail": "Docker appears multiple times in the job description",
     "priority": "high"
   }
 ]
}
```

---

# 🔒 Privacy & Security

✔ No resumes stored
✔ No database usage
✔ No tracking or analytics
✔ API keys remain local

All data is processed **in memory only**.

---

# 🤝 Contributing

Pull requests are welcome.

Steps:

```
Fork → Create Branch → Commit → Push → PR
```

Example:

```
git checkout -b feature/improvement
```

---

# 📄 License

MIT License

See `LICENSE` file.

---

# 👨‍💻 Author

**Bala Dharmaraju**

GitHub
[https://github.com/chbaladharmaraju](https://github.com/chbaladharmaraju)

---

⭐ **If you like this project, please star the repo!**


