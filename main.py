from flask import Flask, request, render_template
import os
import re
import pdfplumber
import docx2txt
from markupsafe import Markup
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/'


# ---------------------------------------------------
# CLEAN GARBAGE (REMOVE ONLY BAD TEXT, NOT <br>)
# ---------------------------------------------------
def clean_garbage(text):
    if not text:
        return ""

    # Remove CSS garbage
    text = re.sub(r'background\s*:\s*[^;"<>\s]+', '', text, flags=re.IGNORECASE)
    text = re.sub(r'color\s*:\s*[^;"<>\s]+', '', text, flags=re.IGNORECASE)
    text = re.sub(r'background\s*:\s*[^">]+', '', text, flags=re.IGNORECASE)
    text = re.sub(r'color\s*:\s*[^">]+', '', text, flags=re.IGNORECASE)

    # Remove HTML tags EXCEPT <br>
    text = re.sub(r'<(?!br\s*\/?)[^>]+>', '', text)

    return text


# ---------------------------------------------------
# PDF TEXT EXTRACTION (line breaks kept)
# ---------------------------------------------------
def extract_text_from_pdf(path):
    text = ""
    try:
        with pdfplumber.open(path) as pdf:
            for page in pdf.pages:
                raw = page.extract_text()

                if raw:
                    raw = raw.replace("\r", "\n")
                    raw = raw.replace("•", "- ")
                    raw = raw.replace("\u2022", "- ")

                    raw = re.sub(r"[ ]{2,}", " ", raw)

                    text += raw + "\n"
    except Exception as e:
        print("PDF ERROR:", e)

    return text


# ---------------------------------------------------
# DOCX + TXT EXTRACTION
# ---------------------------------------------------
def extract_text_from_docx(path):
    try:
        return docx2txt.process(path) or ""
    except:
        return ""


def extract_text_from_txt(path):
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    except:
        return ""


def extract_text(path):
    low = path.lower()
    if low.endswith(".pdf"):
        return extract_text_from_pdf(path)
    elif low.endswith(".docx"):
        return extract_text_from_docx(path)
    elif low.endswith(".txt"):
        return extract_text_from_txt(path)
    return ""


# ---------------------------------------------------
# HIGHLIGHT KEYWORDS (NO CLEANING INSIDE)
# ---------------------------------------------------
def highlight_keywords(text, jd):
    tokens = re.findall(r"[A-Za-z0-9\+\#\.]{2,}", jd.lower())

    stopwords = {
        "and", "with", "for", "from", "the", "you", "are", "will",
        "your", "but", "this", "that", "have", "has", "our", "job",
        "role", "skills", "requirements", "years", "experience",
        "or", "in", "to", "if", "of", "a", "as", "an"
    }

    keywords = [t for t in tokens if t not in stopwords]
    keywords = list(dict.fromkeys(keywords))
    keywords.sort(key=len, reverse=True)

    safe = text

    for kw in keywords:
        safe = re.sub(
            rf"({re.escape(kw)})",
            r'<mark class="hl">\1</mark>',
            safe,
            flags=re.IGNORECASE
        )

    return Markup(safe)


# ---------------------------------------------------
# TF-IDF SCORE
# ---------------------------------------------------
def analyze_score(jd, resume):
    vectorizer = TfidfVectorizer(stop_words="english")
    try:
        vecs = vectorizer.fit_transform([jd, resume]).toarray()
        score = cosine_similarity([vecs[0]], [vecs[1]])[0][0]
    except:
        score = 0
    return round(score * 100, 2)


# ---------------------------------------------------
# ROUTES
# ---------------------------------------------------
@app.route("/")
@app.route("/upload")
def upload_page():
    return render_template("matchresume.html")

@app.route("/dashboard")
def dashboard():

    import os, json

    scores_file = "data/scores.json"

    # Load scores
    if os.path.exists(scores_file):
        with open(scores_file, "r") as f:
            all_scores = json.load(f)
    else:
        all_scores = []

    # If empty, define defaults
    if len(all_scores) == 0:
        total_resumes = 0
        top_score = 0
        avg_score = 0
        min_score = 0
        recent_uploads = []
        upload_dates = []
        upload_counts = []
        return render_template(
            "dashboard.html",
            total_resumes=total_resumes,
            top_score=top_score,
            avg_score=avg_score,
            min_score=min_score,
            recent_uploads=recent_uploads,
            upload_dates=upload_dates,
            upload_counts=upload_counts
        )

    # Stats
    score_list = [i["score"] for i in all_scores]

    total_resumes = len(all_scores)
    top_score = max(score_list)
    avg_score = sum(score_list) / len(score_list)
    min_score = min(score_list)

    # Recent uploads
    recent_uploads = all_scores[-5:][::-1]

    # Chart data
    date_count = {}  # {"2025-01-12": 3}

    for i in all_scores:
        d = i["date"][:10]
        date_count[d] = date_count.get(d, 0) + 1

    upload_dates = list(date_count.keys())
    upload_counts = list(date_count.values())

    return render_template(
        "dashboard.html",
        total_resumes=total_resumes,
        top_score=top_score,
        avg_score=avg_score,
        min_score=min_score,
        recent_uploads=recent_uploads,
        upload_dates=upload_dates,
        upload_counts=upload_counts
    )



@app.route("/history")
def history():

    sample_history = [
        {
            "filename": "resume1.pdf",
            "score": 89.5,
            "date": "2026-06-06 14:00"
        },
        {
            "filename": "resume2.docx",
            "score": 75.2,
            "date": "2026-06-06 14:05"
        }
    ]

    return render_template(
        "history.html",
        history=sample_history
    )

@app.route("/settings")
def settings():
    return render_template("settings.html")

@app.route("/matcher", methods=["POST"])
def matcher():

    jd = request.form.get("job_description", "").strip()
    resume_files = request.files.getlist("resumes")

    print("=" * 50)
    print("JOB DESCRIPTION RECEIVED:", len(jd))
    print("FILES RECEIVED:", len(resume_files))
    print("=" * 50)

    if not jd:
        return render_template(
            "matchresume.html",
            message="Please enter a job description"
        )

    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    extracted = []

    for f in resume_files:

        if not f.filename:
            continue

        print("\nProcessing:", f.filename)

        save_path = os.path.join(
            app.config["UPLOAD_FOLDER"],
            f.filename
        )

        f.save(save_path)

        raw = extract_text(save_path)

        print("Extracted Characters:", len(raw))

        raw = clean_garbage(raw)

        if raw.strip():

            preview = raw[:3000]

            extracted.append((
                f.filename,
                raw,
                preview
            ))

            print("SUCCESS:", f.filename)

        else:
            print("FAILED TO EXTRACT:", f.filename)

    print("\nTOTAL EXTRACTED:", len(extracted))

    if not extracted:
        return render_template(
            "matchresume.html",
            message="No readable resumes found"
        )

    results = []
    scores = []

    for filename, full_text, preview in extracted:

        preview_html = (
            preview
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace("\n", "<br>")
        )

        final_preview = highlight_keywords(
            preview_html,
            jd
        )

        score = analyze_score(
            jd,
            full_text
        )

        scores.append(score)

        results.append({
            "filename": filename,
            "score": score,
            "preview": final_preview
        })

    print("RESULT COUNT:", len(results))

    results.sort(
        key=lambda x: x["score"],
        reverse=True
    )

    stats = {
        "total": len(scores),
        "min": min(scores),
        "max": max(scores),
        "average": round(
            sum(scores) / len(scores),
            2
        )
    }

    return render_template(
        "matchresume.html",
        results=results,
        stats=stats
    )

if __name__ == "__main__":
    app.run(debug=True)
