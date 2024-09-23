import os
import re
import boto3
from db import get_connection
from embedding import create_retriever, read_pdf_file
from bs4 import BeautifulSoup

from botocore.handlers import disable_signing


def import_data_s3(args):
    conn = get_connection()
    with conn:
        with conn.cursor() as curs:
            # Configure s3 b
            curs.execute(
                f"""SELECT aidb.create_s3_retriever(
                    'html_file_embeddings', -- Name of the similarity retrieval setup
                    'public', -- Schema of the source table
                    '{os.getenv("AIDB_MODEL_NAME")}', -- Embeddings encoder model for retriever
                    'text',
                    '{args.bucket_name}',
                    '',
                    'http://s3.eu-central-1.amazonaws.com'
                    );"""
            )
            curs.execute("""SELECT aidb.refresh_retriever('html_file_embeddings');""")
            s3_text_to_table(curs, args.bucket_name)
        conn.commit()
    conn.close()
    print(
        "import-data-s3 command executed. S3 bucket name: {}".format(args.bucket_name)
    )

def update_s3_data(args):
    conn = get_connection()
    with conn:
        with conn.cursor() as curs:
            # Store each embedding in the database
            curs.execute(f"""SELECT aidb.refresh_retriever('{args.retriever_name}');""")
            s3_text_to_table(curs, args.bucket_name)
    conn.commit()
    conn.close()
    print(
        "update-data-s3 command executed. S3 bucket name: {}".format(args.bucket_name)
    )

def connect_to_s3():
    # it's assumed that the s3 bucket is public for this demo
    # change the authentication or the endpoint url to authenticate to a different bucket
    s3 = boto3.resource(
                service_name="s3",
                endpoint_url='http://s3.eu-central-1.amazonaws.com',
            )
    s3.meta.client.meta.events.register("choose-signer.s3.*", disable_signing)
    return s3

def count_rows(cursor):
    # count row numbers to define the id value for PK
    cursor.execute("SELECT COUNT(*) filename FROM documents;")
    return cursor.fetchone()[0]


def pdf_to_table(cursor, file_path, filename):
    # read pdf in fragments and insert to documents table
    data = read_pdf_file(file_path)
    # Store each embedding in the database
    
    for i, doc_fragment in enumerate(data):
        cursor.execute(
            "INSERT INTO documents (filename, doc_fragment) VALUES (%s, %s, %s) ON CONFLICT (filename)",
            (filename, doc_fragment),
        )
    return i


def s3_text_to_table(cursor, bucket_name):
    # read pdf in fragments and insert to documents table
    s3 = connect_to_s3()
    file_list = [
                f
                for f in s3.Bucket(bucket_name).objects.filter(Prefix="")
            ]
    
    for i, file in enumerate(file_list):
        file_context = file.get()["Body"].read()
        filename, _ = os.path.splitext(file.key)
        text_content = file_context.decode(encoding="utf-8", errors="ignore")
        # Extract the HTML body content
        soup = BeautifulSoup(text_content, 'html.parser')
        body_content = soup.body.get_text(separator="\n") if soup.body else ""
        # Remove excessive whitespace but keep structure
        body_content = re.sub(r'\s+', ' ', body_content).strip()
    
        cursor.execute(
            """INSERT INTO documents (filename, doc_fragment) VALUES (%s, %s) ON CONFLICT (filename)
            DO UPDATE SET doc_fragment = EXCLUDED.doc_fragment;""",
            (filename, body_content),
        )
        
    return None


def import_data_pg(args):
    conn = get_connection()
    with conn:
        with conn.cursor() as curs:
            # get already existing rows in documents table
            curs.execute("SELECT DISTINCT filename FROM documents;")
            existing_filenames = {result[0] for result in curs.fetchall()}
            # no data is in documents
            if count_rows(curs) == 0:
                create_retriever()
            # Process the files in the directory
            for full_filename in os.listdir(args.data_dir):
                filename, _ = os.path.splitext(full_filename)
                if filename not in existing_filenames:
                    file_path = os.path.join(args.data_dir, full_filename)
                    
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                        file_content = file.read()
                    
                    soup = BeautifulSoup(file_content, 'html.parser')
                    body_content = soup.body.get_text(separator="\n") if soup.body else ""
                    body_content = re.sub(r'\s+', ' ', body_content).strip()
                    
                    # Store each embedding in the database
                    curs.execute(
                    """INSERT INTO documents (filename, doc_fragment) VALUES (%s, %s);""",
                    (filename, body_content),
                )
    conn.commit()
    conn.close()
    print("import-data-pg command executed. Data dir: {}".format(args.data_dir))
    


def import_data_pg_pdf(args):
    conn = get_connection()
    with conn:
        with conn.cursor() as curs:
            # get already existing rows in documents table
            curs.execute("SELECT DISTINCT filename FROM documents;")
            existing_filenames = {result[0] for result in curs.fetchall()}

            # List all files in the directory
            start_index = count_rows(curs)  # Get the current count of rows
            # Flag to check if documents table was empty initially
            was_empty = start_index == 0
            # Process the files in the directory
            for full_filename in os.listdir(args.data_dir):
                # remove extension
                filename, _ = os.path.splitext(full_filename)
                if filename not in existing_filenames:
                    file_path = os.path.join(args.data_dir, full_filename)
                    
                    pdf_to_table(curs, file_path, filename)
    conn.commit()
    # Call create_retriever() if the documents table was empty initially
    if was_empty:
        create_retriever()
        print("import-data-pg command executed. Data dir: {}".format(args.data_dir))
