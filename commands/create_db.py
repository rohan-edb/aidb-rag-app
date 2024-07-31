import os
import psycopg2


def create_db(args):
    db_config = {
        "user": os.getenv("DB_USER"),
        "password": os.getenv("DB_PASSWORD"),
        "host": os.getenv("DB_HOST"),
        "port": os.getenv("DB_PORT"),
    }

    conn = psycopg2.connect(**db_config)
    conn.autocommit = True  # Enable autocommit for creating the database

    cursor = conn.cursor()
    cursor.execute(
        f"SELECT 1 FROM pg_database WHERE datname = '{os.getenv('DB_NAME')}';"
    )
    database_exists = cursor.fetchone()
    cursor.close()

    if not database_exists:
        cursor = conn.cursor()
        cursor.execute(f"CREATE DATABASE {os.getenv('DB_NAME')};")
        cursor.close()
        print("Database created.")

    conn.close()
    db_config["dbname"] = os.getenv("DB_NAME")
    conn = psycopg2.connect(**db_config)
    conn.autocommit = True

    cursor = conn.cursor()
    cursor.execute("CREATE EXTENSION IF NOT EXISTS aidb cascade;")
    cursor.close()

    cursor = conn.cursor()
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS documents (id text PRIMARY KEY, doc_fragment text);"
    )
    cursor.close()

    print("Database setup completed.")
