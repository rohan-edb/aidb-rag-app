import os
import PyPDF2
from db import get_connection

def create_retriever():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(f"""
                    SELECT aidb.create_pg_retriever(
                        'documents_embeddings',
                        'public',
                        'id',
                        '{os.getenv("AIDB_MODEL_NAME")}',
                        'text',
                        'documents',
                        ARRAY['filename', 'doc_fragment'],
                        TRUE);""")
    conn.commit()
    return None


def read_pdf_file(pdf_path):
    pdf_document = PyPDF2.PdfReader(pdf_path)

    lines = []
    for page_number in  range(len(pdf_document.pages)):
        page = pdf_document.pages[page_number]

        text = page.extract_text()

        lines.extend(text.splitlines())

    return lines
