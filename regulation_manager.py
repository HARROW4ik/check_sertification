import os
from docx import Document
import pdfplumber

class RegulationManager:
    def __init__(self):
        self.regulations = {}

    def load_regulations(self, regulations_folder):
        for filename in os.listdir(regulations_folder):
            if filename.endswith(".docx"):
                self.load_from_docx(os.path.join(regulations_folder, filename))
            elif filename.endswith(".pdf"):
                self.load_from_pdf(os.path.join(regulations_folder, filename))

    def load_from_docx(self, file_path):
        doc = Document(file_path)
        self.regulations[file_path] = "\n".join([para.text.strip() for para in doc.paragraphs if para.text.strip()])

    def load_from_pdf(self, file_path):
        with pdfplumber.open(file_path) as pdf:
            content = []
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    content.append(text)
            self.regulations[file_path] = "\n".join(content)

    def get_regulations(self):
        return self.regulations
