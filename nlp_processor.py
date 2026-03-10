"""
NLP Processor Module
--------------------
Pure-Python NLP utilities for resume and job description analysis.
Uses text processing techniques (tokenisation, TF-IDF-style scoring,
keyword extraction) without heavy external NLP libraries.
"""

import re
import math
from collections import Counter


# ---------------------------------------------------------------------------
# Common English stop-words (compact set – good enough for keyword work)
# ---------------------------------------------------------------------------
STOP_WORDS = set(
    "a an the and or but in on at to for of is it that this with as by from "
    "are was were be been being have has had do does did will would shall should "
    "may might can could about above after again against all am any because "
    "before below between both during each few further get got he her here hers "
    "herself him himself his how i if into just me more most my myself no nor "
    "not now off once only other our ours ourselves out over own re s same she "
    "so some such t than them then there these they their theirs themselves "
    "through too under until up very we what when where which while who whom "
    "why you your yours yourself yourselves able also already always among "
    "another even every however many much must never new often old one still "
    "two us using well within without work working worked experience including "
    "using used use".split()
)

# ---------------------------------------------------------------------------
# Tech / skill keyword dictionary for smarter extraction
# ---------------------------------------------------------------------------
TECH_KEYWORDS = set(
    "python java javascript typescript react angular vue node nodejs express flask django "
    "fastapi spring springboot dotnet csharp c++ golang rust swift kotlin ruby php "
    "html css sass tailwind bootstrap jquery nextjs nuxt svelte "
    "sql nosql mysql postgresql postgres mongodb redis elasticsearch dynamodb "
    "aws azure gcp google cloud firebase heroku docker kubernetes k8s terraform "
    "ansible jenkins github gitlab ci cd cicd devops mlops dataops "
    "git linux bash powershell nginx apache "
    "tensorflow pytorch keras scikit sklearn pandas numpy scipy matplotlib seaborn "
    "jupyter notebook spark hadoop airflow kafka rabbitmq celery "
    "rest api graphql grpc microservices serverless lambda "
    "agile scrum kanban jira confluence figma sketch "
    "machine learning deep learning nlp computer vision ai artificial intelligence "
    "data science data engineering analytics bi tableau powerbi looker "
    "blockchain solidity web3 "
    "ios android mobile react native flutter "
    "unit testing integration testing selenium cypress jest mocha pytest "
    "oauth jwt saml sso security encryption ssl tls "
    "excel powerpoint word sharepoint salesforce sap erp crm "
    "communication leadership teamwork problem solving project management".split()
)


def _tokenize(text: str) -> list[str]:
    """Lowercase, strip punctuation, split into word tokens."""
    text = text.lower()
    text = re.sub(r"[^a-z0-9#+.\-/]", " ", text)
    tokens = text.split()
    return [t for t in tokens if len(t) > 1]


def _extract_ngrams(tokens: list[str], n: int = 2) -> list[str]:
    """Generate n-grams from a token list."""
    return [" ".join(tokens[i : i + n]) for i in range(len(tokens) - n + 1)]


def extract_keywords(text: str, top_n: int = 40) -> list[str]:
    """
    Extract meaningful keywords / phrases from text.
    Combines single-word tech terms and bi-grams weighted by frequency.
    """
    tokens = _tokenize(text)
    # Single words – keep only non-stop-words
    singles = [t for t in tokens if t not in STOP_WORDS and len(t) > 2]
    # Bi-grams
    bigrams = _extract_ngrams(tokens, 2)
    bigrams = [b for b in bigrams if not all(w in STOP_WORDS for w in b.split())]

    freq = Counter(singles)
    # Boost known tech terms
    for token in freq:
        if token in TECH_KEYWORDS:
            freq[token] *= 3

    bigram_freq = Counter(bigrams)
    for bg in bigram_freq:
        if any(w in TECH_KEYWORDS for w in bg.split()):
            bigram_freq[bg] *= 2

    combined = freq + bigram_freq
    return [kw for kw, _ in combined.most_common(top_n)]


def compute_keyword_overlap(resume_keywords: list[str], jd_keywords: list[str]):
    """
    Compute keyword overlap between resume and JD.
    Returns matched, missing, and a 0-100 ATS score.
    """
    resume_set = set(k.lower() for k in resume_keywords)
    jd_set = set(k.lower() for k in jd_keywords)

    matched = sorted(resume_set & jd_set)
    missing = sorted(jd_set - resume_set)

    if not jd_set:
        ats_score = 0
    else:
        ats_score = round(len(matched) / len(jd_set) * 100)

    return matched, missing, min(ats_score, 100)


def compute_similarity(text_a: str, text_b: str) -> int:
    """
    Compute a cosine-similarity-inspired match percentage between two texts
    using TF weighting on their token vectors.
    Returns 0-100 integer.
    """
    tokens_a = [t for t in _tokenize(text_a) if t not in STOP_WORDS and len(t) > 2]
    tokens_b = [t for t in _tokenize(text_b) if t not in STOP_WORDS and len(t) > 2]

    if not tokens_a or not tokens_b:
        return 0

    freq_a = Counter(tokens_a)
    freq_b = Counter(tokens_b)

    # All unique terms
    all_terms = set(freq_a.keys()) | set(freq_b.keys())

    # Cosine similarity
    dot = sum(freq_a.get(t, 0) * freq_b.get(t, 0) for t in all_terms)
    mag_a = math.sqrt(sum(v ** 2 for v in freq_a.values()))
    mag_b = math.sqrt(sum(v ** 2 for v in freq_b.values()))

    if mag_a == 0 or mag_b == 0:
        return 0

    similarity = dot / (mag_a * mag_b)
    return min(round(similarity * 100), 100)


def extract_email(text: str) -> str | None:
    """Extract the first email address found."""
    match = re.search(r"[\w.+-]+@[\w-]+\.[\w.-]+", text)
    return match.group(0) if match else None


def extract_phone(text: str) -> str | None:
    """Extract the first phone number found."""
    match = re.search(r"[\+]?[\d\s\-().]{7,15}", text)
    return match.group(0).strip() if match else None


def extract_sections(text: str) -> dict:
    """
    Best-effort extraction of common resume sections by header matching.
    Returns a dict with section name → content snippets.
    """
    section_patterns = [
        ("contact", r"(?i)(contact|email|phone|address)"),
        ("summary", r"(?i)(summary|objective|profile|about)"),
        ("experience", r"(?i)(experience|employment|work\s*history)"),
        ("education", r"(?i)(education|academic|university|degree)"),
        ("skills", r"(?i)(skills|technologies|technical|competenc)"),
        ("certifications", r"(?i)(certif|licen|accredit)"),
        ("projects", r"(?i)(project)"),
    ]

    lines = text.split("\n")
    sections: dict[str, list[str]] = {}
    current_section = "other"

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        for name, pattern in section_patterns:
            if re.search(pattern, stripped) and len(stripped) < 60:
                current_section = name
                break
        sections.setdefault(current_section, []).append(stripped)

    return {k: "\n".join(v[:20]) for k, v in sections.items()}
