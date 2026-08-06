# 🩺 MedIntel AI

AI-powered Medical Report Analyzer built with **Python, Streamlit, OCR, Groq LLM, and MySQL** to analyze medical reports, detect abnormalities, identify health risks, and provide AI-generated clinical insights.

🌐 Live Demo: https://medintel-ai-4shtmxtbscmciy5ja2hpho.streamlit.app/

---

# Features

- Secure User Login & Authentication
- Upload Medical Reports (PDF)
- Upload Medical Images from Mobile Gallery
- OCR Support for Scanned Reports
- Automatic Clinical Parameter Extraction
- Normal & Abnormal Value Detection
- Risk Factor Identification
- Preliminary Disease Prediction
- AI-Powered Medical Report Analysis (Groq LLM)
- Specialist Recommendation
- Patient History Management
- Downloadable PDF Report
- Responsive Mobile-Friendly UI
- Streamlit Cloud Deployment

---

# Technologies Used

### Programming Language
- Python

### Frontend
- Streamlit

### AI & Machine Learning
- Groq LLM API
- Prompt Engineering

### OCR & Document Processing
- PyMuPDF
- PDFPlumber
- PyTesseract
- Pillow

### Database
- MySQL

### Libraries
- Pandas
- NumPy
- Matplotlib
- Scikit-learn
- ReportLab

### Version Control
- Git
- GitHub

---

# Project Workflow

1. User uploads a medical report (PDF or image).
2. OCR extracts text from scanned reports.
3. Clinical parameters are extracted automatically.
4. Values are compared with normal reference ranges.
5. Risk factors are identified.
6. Preliminary health conditions are predicted.
7. Groq LLM generates an easy-to-understand medical summary.
8. Suitable medical specialist is recommended.
9. User can download the final report as a PDF.

---

# Folder Structure

```
MedIntel-AI/
│
├── app.py
├── requirements.txt
├── packages.txt
├── README.md
│
├── llm/
│   └── groq_service.py
│
├── ml/
│   └── predictor.py
│
├── utils/
│   ├── analyzer.py
│   ├── dashboard.py
│   ├── normal_ranges.py
│   ├── patient.py
│   ├── pdf_generator.py
│   ├── pdf_reader.py
│   ├── preprocess.py
│   ├── risk_factors.py
│   └── specialist.py
```

---

# Installation

Clone the repository

```bash
git clone https://github.com/boddugideon/MedIntel-AI.git
```

Move into the project folder

```bash
cd MedIntel-AI
```

Install dependencies

```bash
pip install -r requirements.txt
```

Run the application

```bash
streamlit run app.py
```

---

# Future Improvements

- Multi-language medical report analysis
- Medical chatbot
- X-ray and MRI image analysis
- Cloud storage for patient reports
- Appointment booking integration
- Advanced disease prediction models

---

# Skills Demonstrated

- Python Development
- AI Integration
- OCR Processing
- Prompt Engineering
- LLM Integration
- Medical Data Processing
- Streamlit Application Development
- MySQL Database
- Git & GitHub
- API Integration
- PDF Generation
- Responsive UI Design

---

# Author

**Boddu Gideon**

📧 Email: gideonboddu@gmail.com

🔗 LinkedIn: https://www.linkedin.com/in/boddu-gideon-a65062350/

💻 GitHub: https://github.com/boddugideon

---

# License

This project is developed for educational and learning purposes.
