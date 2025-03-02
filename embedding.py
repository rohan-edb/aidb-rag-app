import os
import PyPDF2
from db import get_connection

def create_retriever():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(f"""
                    SELECT aidb.create_retriever_for_table(
                        name => 'documents_embeddings',
                        model_name => '{os.getenv("AIDB_MODEL_NAME")}',
                        source_table => 'documents',
                        source_data_column => 'doc_fragment',
                        source_data_type => 'Text'
                        );""")
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
