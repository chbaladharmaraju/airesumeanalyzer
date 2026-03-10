"""
AI Resume Analyzer — Flask Backend
-----------------------------------
Serves the frontend and provides /api/analyze endpoint
that parses resumes, runs NLP analysis, and calls Gemini API.
"""

import os
import json
import time
import traceback

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv
import google.generativeai as genai

from nlp_processor import (
    extract_keywords,
    compute_keyword_overlap,
    compute_similarity,
    extract_email,
    extract_phone,
    extract_sections,
)

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

app = Flask(__name__, static_folder="static", static_url_path="")
CORS(app)

ALLOWED_EXTENSIONS = {"pdf", "docx", "txt"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB


# ---------------------------------------------------------------------------
# File Parsing Helpers
# ---------------------------------------------------------------------------
def _allowed(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def parse_file(file_storage) -> str:
    """Extract plain text from uploaded PDF, DOCX, or TXT file."""
    filename = file_storage.filename or ""
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""

    raw = file_storage.read()

    if ext == "pdf":
        import PyPDF2
        import io
        reader = PyPDF2.PdfReader(io.BytesIO(raw))
        pages = [p.extract_text() or "" for p in reader.pages]
        return "\n".join(pages).strip()

    elif ext == "docx":
        import docx
        import io
        doc = docx.Document(io.BytesIO(raw))
        return "\n".join(p.text for p in doc.paragraphs).strip()

    elif ext == "txt":
        return raw.decode("utf-8", errors="ignore").strip()

    else:
        raise ValueError(f"Unsupported file type: .{ext}")


# ---------------------------------------------------------------------------
# Gemini Integration
# ---------------------------------------------------------------------------
# Maximum retries and backoff settings for Gemini API
MAX_RETRIES = 3
BASE_DELAY = 1  # seconds


def call_gemini(resume_text: str, jd_text: str, nlp_data: dict) -> dict:
    """
    Send a structured prompt to Gemini and parse the JSON response.
    Includes automatic retry with exponential backoff for rate-limit errors.
    """
    if not GEMINI_API_KEY or GEMINI_API_KEY == "your_api_key_here":
        raise EnvironmentError(
            "GEMINI_API_KEY is not set. Please add it to your .env file."
        )

    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel("gemini-2.5-flash")

    prompt = f"""You are an expert career advisor and ATS (Applicant Tracking System) specialist.

TASK: Analyse the resume against the job description. Use the NLP pre-analysis data provided and your own deeper understanding to produce a comprehensive, actionable report.

=== RESUME TEXT ===
{resume_text[:8000]}

=== JOB DESCRIPTION ===
{jd_text[:5000]}

=== NLP PRE-ANALYSIS ===
ATS Keyword Score: {nlp_data.get('ats_score', 0)}/100
Text Similarity Score: {nlp_data.get('similarity_score', 0)}/100
Matched Keywords: {json.dumps(nlp_data.get('matched_keywords', []))}
Missing Keywords: {json.dumps(nlp_data.get('missing_keywords', []))}
Detected Email: {nlp_data.get('email', 'N/A')}
Detected Phone: {nlp_data.get('phone', 'N/A')}

INSTRUCTIONS:
1. Refine the ATS score (0-100) considering keyword importance and context, not just raw overlap. Use the NLP score as a baseline.
2. Provide a semantic match percentage (0-100) reflecting how well the candidate's overall profile fits the role semantically (experience level, domain, responsibilities).
3. Identify the top matched strengths (areas where resume strongly aligns with JD).
4. Identify missing/weak areas.
5. Generate exactly 10 concrete, actionable improvement suggestions. Each suggestion must be specific — reference actual resume content and JD requirements. Examples:
   - "Add 'Kubernetes' to your skills section — it appears 4 times in the JD"
   - "Quantify your AWS achievement: change 'Managed cloud infrastructure' to 'Managed AWS infrastructure for 50+ microservices, reducing costs by 22%'"
   - "Add a 'Certifications' section — the JD requires AWS Solutions Architect certification"

Return ONLY valid JSON (no markdown fences, no extra text) in this exact structure:
{{
  "ats_score": <int 0-100>,
  "semantic_match": <int 0-100>,
  "resume_summary": "<2-3 sentence summary of the candidate's profile>",
  "jd_summary": "<2-3 sentence summary of what the JD requires>",
  "matched_keywords": ["keyword1", "keyword2", ...],
  "missing_keywords": ["keyword1", "keyword2", ...],
  "strengths": ["strength1", "strength2", ...],
  "suggestions": [
    {{
      "title": "<short title>",
      "detail": "<specific, actionable recommendation>",
      "priority": "<high|medium|low>"
    }}
  ]
}}
"""

    last_exception = None

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = model.generate_content(prompt)
            text = response.text.strip()

            # Strip markdown code fences if present
            if text.startswith("```"):
                text = text.split("\n", 1)[1] if "\n" in text else text[3:]
            if text.endswith("```"):
                text = text[:-3]
            text = text.strip()
            if text.startswith("json"):
                text = text[4:].strip()

            return json.loads(text)

        except Exception as e:
            last_exception = e
            error_msg = str(e).lower()
            is_rate_limit = (
                "429" in str(e)
                or "resource exhausted" in error_msg
                or "quota" in error_msg
                or "rate limit" in error_msg
                or "too many requests" in error_msg
            )

            if is_rate_limit and attempt < MAX_RETRIES:
                delay = BASE_DELAY * (2 ** (attempt - 1))  # 1s, 2s, 4s
                print(f"⚠️  Rate limited (attempt {attempt}/{MAX_RETRIES}). "
                      f"Retrying in {delay}s...")
                time.sleep(delay)
                continue

            # Not a rate-limit error or final attempt — re-raise
            raise


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
@app.route("/")
def index():
    return send_from_directory("static", "index.html")


@app.route("/api/analyze", methods=["POST"])
def analyze():
    try:
        # --- Validate inputs ---
        if "resume" not in request.files:
            return jsonify({"error": "No resume file uploaded."}), 400

        file = request.files["resume"]
        if not file or not file.filename:
            return jsonify({"error": "Empty file."}), 400

        if not _allowed(file.filename):
            return jsonify({
                "error": f"Unsupported file type. Please upload PDF, DOCX, or TXT."
            }), 400

        jd_text = request.form.get("job_description", "").strip()
        if not jd_text:
            return jsonify({"error": "Job description is required."}), 400

        # --- Parse resume ---
        try:
            resume_text = parse_file(file)
        except Exception as e:
            return jsonify({"error": f"Failed to parse file: {str(e)}"}), 400

        if len(resume_text) < 50:
            return jsonify({
                "error": "Resume text is too short or could not be extracted. Please try a different file."
            }), 400

        # --- NLP Analysis ---
        resume_keywords = extract_keywords(resume_text)
        jd_keywords = extract_keywords(jd_text)
        matched, missing, ats_score = compute_keyword_overlap(resume_keywords, jd_keywords)
        similarity = compute_similarity(resume_text, jd_text)
        email = extract_email(resume_text)
        phone = extract_phone(resume_text)
        sections = extract_sections(resume_text)

        nlp_data = {
            "ats_score": ats_score,
            "similarity_score": similarity,
            "matched_keywords": matched,
            "missing_keywords": missing,
            "email": email,
            "phone": phone,
            "resume_sections": sections,
            "resume_keywords": resume_keywords,
            "jd_keywords": jd_keywords,
        }

        # --- Gemini API (with automatic retry for 429s) ---
        try:
            gemini_result = call_gemini(resume_text, jd_text, nlp_data)
        except EnvironmentError as e:
            return jsonify({"error": str(e)}), 500
        except json.JSONDecodeError:
            return jsonify({
                "error": "Gemini returned an invalid response. Please try again."
            }), 502
        except Exception as e:
            error_msg = str(e).lower()
            is_rate_limit = (
                "429" in str(e)
                or "resource exhausted" in error_msg
                or "quota" in error_msg
                or "rate limit" in error_msg
                or "too many requests" in error_msg
            )
            if is_rate_limit:
                return jsonify({
                    "error": "API rate limit reached. All retry attempts exhausted. Please wait a minute and try again.",
                    "error_type": "rate_limit"
                }), 429
            return jsonify({"error": f"AI analysis failed: {str(e)}"}), 503

        # --- Merge NLP + Gemini results ---
        result = {
            "ats_score": gemini_result.get("ats_score", ats_score),
            "semantic_match": gemini_result.get("semantic_match", similarity),
            "resume_summary": gemini_result.get("resume_summary", ""),
            "jd_summary": gemini_result.get("jd_summary", ""),
            "matched_keywords": gemini_result.get("matched_keywords", matched),
            "missing_keywords": gemini_result.get("missing_keywords", missing),
            "strengths": gemini_result.get("strengths", []),
            "suggestions": gemini_result.get("suggestions", []),
            "nlp_details": {
                "email": email,
                "phone": phone,
                "sections_found": list(sections.keys()),
                "raw_ats_score": ats_score,
                "raw_similarity": similarity,
            },
        }

        return jsonify(result), 200

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print("🚀 AI Resume Analyzer running at http://localhost:5000")
    app.run(debug=True, port=5000)
