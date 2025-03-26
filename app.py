import os
import fitz  # PyMuPDF for PDF handling
import docx2txt
import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv

# Load API key from .env file
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Ensure API key is set
if not GOOGLE_API_KEY:
    st.error("⚠️ Google API key is missing! Please set it in a .env file.")
    st.stop()

# Configure Google AI
genai.configure(api_key=GOOGLE_API_KEY)

# Function to extract text from PDF
def extract_text_from_pdf(pdf_file):
    text = ""
    try:
        with fitz.open(stream=pdf_file.getbuffer(), filetype="pdf") as pdf_document:
            for page in pdf_document:
                text += page.get_text()
    except Exception as e:
        st.error(f"⚠️ Error reading PDF file: {e}")
    return text

# Function to extract text from DOCX
def extract_text_from_docx(docx_file):
    try:
        return docx2txt.process(docx_file)
    except Exception as e:
        st.error(f"⚠️ Error reading DOCX file: {e}")
        return ""

# Function to analyze resume using Google Gemini AI
def analyze_resume(resume_text):
    if not resume_text.strip():
        return "⚠️ No text found in the resume. Please upload a valid resume."

    prompt = f"""
    You are an AI-powered resume reviewer. Analyze the following resume and provide:
    1️⃣ Strengths  
    2️⃣ Weaknesses  
    3️⃣ Suggestions for improvement  

    Resume Text:
    {resume_text}
    """

    try:
        model = genai.GenerativeModel("gemini-1.5-pro")  # Ensure correct model name
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"⚠️ Error analyzing resume: {e}"

# Streamlit UI
st.title("📄 AI-Powered Resume Analyzer")
st.write("Upload your resume (PDF or DOCX), and the AI will provide feedback!")

# File uploader
uploaded_file = st.file_uploader("Upload Resume", type=["pdf", "docx"])

if uploaded_file is not None:
    file_type = uploaded_file.name.split(".")[-1]

    # Extract text from uploaded resume
    if file_type == "pdf":
        resume_text = extract_text_from_pdf(uploaded_file)
    elif file_type == "docx":
        resume_text = extract_text_from_docx(uploaded_file)
    else:
        st.error("Unsupported file format. Please upload a PDF or DOCX file.")
        st.stop()

    # Check if resume text is extracted
    if not resume_text.strip():
        st.error("⚠️ No text found in the uploaded file. Please upload a valid resume.")
        st.stop()

    # Display extracted resume text
    st.subheader("📜 Extracted Resume Text:")
    st.text_area("", resume_text, height=200)

    # Button to analyze resume
    if st.button("🚀 Analyze Resume"):
        st.subheader("📝 AI Analysis & Feedback:")
        analysis = analyze_resume(resume_text)
        st.write(analysis)
