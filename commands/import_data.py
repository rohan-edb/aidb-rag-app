from db import get_connection
from embedding import generate_embeddings, read_pdf_file


def import_data(args):
    data = read_pdf_file(args.data_source)
    conn = get_connection()
    cursor = conn.cursor()
    # Store each embedding in the database
    for i, (doc_fragment) in enumerate(data):
        cursor.execute(
            "INSERT INTO documents (id, doc_fragment) VALUES (%s, %s)",
            (i, doc_fragment),
        )
    conn.commit()
    generate_embeddings()
    print(
        "import-data command executed. Data source: {}".format(
            args.data_source
        )
    )

