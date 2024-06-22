import io
import PyPDF2
import docx2txt
import logging
from helpers.blob_storage_utils import get_blob
from helpers.llm_utils import extract_resume_key_details
import os

is_debug = ("debug" in os.environ) and (os.environ["debug"] == "True")

def get_cv_and_analyze(cv_key):
    text = get_cv_content(cv_key)
    text = clean_text(text)
    return get_analysis(text, cv_key)

def get_cv_content(cv_key): 
    try:
        file_content = None
        if is_debug:
            try:
                with open(cv_key, "rb") as fh:
                    file_content = io.BytesIO(fh.read())
            except:
                pass
                
        if file_content == None:
            file_content = get_blob("uploaded-resumes", cv_key)
            file_content = io.BytesIO(file_content)
        return read_document(file_content, cv_key)
    except Exception as e:
        logging.error('Failed to process the CV. %s', e, exc_info=True)
        return None

def read_document(content, file_name):
    if file_name.endswith('.pdf'):
        pdf_text = extract_pdf_text(content)
        return pdf_text
    elif file_name.endswith('.docx'):
        docx_text = extract_docx_text(content)
        return docx_text
    else:
        return 'Unsupported file format'

def clean_text(text):
    if type(text) == bytes:
        text = text.decode("utf-8")
    clean_text = "".join([c if (0x21<=ord(c) and ord(c)<=0x7e) or c == " " else "" for c in text])
    tt = []
    for i in clean_text.split(" "):
        if (len(i) > 0):
            tt.append(i)
    return " ".join(tt)[:5000]

def extract_pdf_text(blob_content):
    pdf_reader = PyPDF2.PdfReader(blob_content)
    text = ""
    for page_num in range(len(pdf_reader.pages)):
        text += pdf_reader.pages[page_num].extract_text()
    text=text.encode('utf-8')
    return text

def extract_docx_text(blob_content):
    document_text = docx2txt.process(blob_content)
    paragraphs = document_text.split('\n\n')
    unique_paragraphs = []
    seen_paragraphs = set()
    for paragraph in paragraphs:
        if paragraph not in seen_paragraphs:
            unique_paragraphs.append(paragraph)
            seen_paragraphs.add(paragraph)
    text = ' '.join(unique_paragraphs)
    return text

def get_analysis(text, cv_key):
    try:
        if len(text.strip()) > 500:
            resume_text = extract_resume_key_details(text)
            extracted_info = get_formatted_data(resume_text, cv_key)
        else:
            extracted_info = None
        return extracted_info
    except Exception as ex:
        logging.error('Failed to fetch the CV. %s', ex, exc_info=True)
        return None

def get_formatted_data(resume_text, cv_key):
    # Splitting the resume text into lines
    lines = resume_text.strip().split('\n')

    # Initializing variables to store extracted data
    experience = None
    location = None
    skills = []
    summary = []
    name = None

    # Flags to indicate when to start capturing summary and skills
    capture_summary = False
    capture_skills = False

    # Iterating through each line to extract relevant information
    for line in lines:
        if line.startswith("Years of Professional Experience:"):
            experience = line.split(":")[1].strip()
        elif line.startswith("Most Recent Work Location:"):
            location = line.split(":")[1].strip()
        elif line.startswith("Work Experience Summary:"):
            capture_summary = True
        elif line.startswith("Skills:"):
            capture_skills = True            
        elif line.startswith("Candidate Name:"):
            name = line.split(":")[1].strip()
        elif capture_summary:
            # Capture summary until the next section starts
            if len(line.strip()) > 0:
                summary.append(line.strip())
            else:
                capture_summary = False
        elif capture_skills:
            # Capture skills until the next section starts
            if line.strip():
                skills.extend([skill.strip() for skill in line.split(",")])
            else:
                capture_skills = False

    # Creating a dictionary to store the extracted information
    extracted_info = {
        "Name": name,
        "Years of Experience": experience,
        "Most Recent Work Location": location,
        "Work Experience Summary": " ".join(summary),
        "Skills": list(set(skills)),
        "Candidate ID": cv_key
    }
    return extracted_info