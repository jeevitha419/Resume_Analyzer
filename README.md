# Resume Analyzer

## Overview

Resume Analyzer is a Flask-based web application that helps recruiters and hiring managers analyze resumes against a job description. The system extracts text from PDF, DOCX, and TXT resumes, calculates similarity scores using TF-IDF and Cosine Similarity, and ranks candidates based on their match percentage.

---

## Features

* Upload multiple resumes at once
* Supports PDF, DOCX, and TXT files
* Job Description matching
* TF-IDF based similarity scoring
* Resume ranking by match percentage
* Keyword highlighting in resume preview
* Dashboard with statistics
* History tracking of analyzed resumes
* Clear History option
* Clear Uploaded Files option
* System Reset option

---

## Technologies Used

### Frontend

* HTML
* CSS
* Bootstrap 5
* JavaScript

### Backend

* Python
* Flask

### Libraries

* pdfplumber
* docx2txt
* scikit-learn
* MarkupSafe

---

## Project Structure

```text
Resume_Analyzer/
│
├── main.py
├── templates/
│   ├── matchresume.html
│   ├── dashboard.html
│   ├── history.html
│   ├── settings.html
│   └── sidebar.html
│
├── static/
│   ├── layout.css
│   └── sidebar.css
│
├── uploads/
├── data/
│   └── scores.json
│
└── README.md
```

---

## Installation

1. Clone the repository

```bash
git clone https://github.com/jeevitha419/Resume_Analyzer.git
```

2. Navigate to the project directory

```bash
cd Resume_Analyzer
```

3. Install dependencies

```bash
pip install flask pdfplumber docx2txt scikit-learn markupsafe
```

---

## Run the Application

```bash
python main.py
```

Open your browser:

```text
http://127.0.0.1:5000
```

---

## How It Works

1. Enter a Job Description.
2. Upload one or more resumes.
3. The system extracts text from resumes.
4. TF-IDF Vectorization is applied.
5. Cosine Similarity calculates matching scores.
6. Results are ranked and displayed.
7. Matching keywords are highlighted.
8. Analysis history is stored for future reference.

---

## Future Enhancements

* AI-powered resume feedback
* Skill gap analysis
* Resume recommendation system
* User authentication
* Database integration
* Export reports as PDF

---

## Author

Jeevitha R

Resume Analyzer Project using Flask and Machine Learning.

