import PyPDF2
import docx
import os

# Extract text from PDF
def extract_text_from_pdf(file_path):
    with open(file_path, "rb") as pdf_file:
        reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        return text

# Extract text from DOCX
def extract_text_from_docx(file_path):
    doc = docx.Document(file_path)
    return "\n".join([para.text for para in doc.paragraphs])

# Unified extraction function
def extract_text(file_path):
    _, ext = os.path.splitext(file_path)
    if ext == ".pdf":
        return extract_text_from_pdf(file_path)
    elif ext == ".docx":
        return extract_text_from_docx(file_path)
    else:
        return "Unsupported file format"

# Test the extraction
if __name__ == "__main__":
    sample_pdf = r"C:\Users\a\OneDrive\Documents\edunet internship\ai-resume-screening\data\sample_resumes\Sankalp Ramteke Resume CCS.pdf"

    sample_docx = r"C:\Users\a\OneDrive\Documents\edunet internship\ai-resume-screening\data\sample_resumes\Sankalp Ramteke Resume CCS.docx"
    print(extract_text(sample_pdf))
    print(extract_text(sample_docx))
