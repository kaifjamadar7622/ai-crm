import os

import psycopg2
from dotenv import load_dotenv

load_dotenv()

conn = None
cursor = None

try:
    conn = psycopg2.connect(
        dbname=os.getenv("DB_NAME", "crm"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432"),
    )
    cursor = conn.cursor()
except Exception:
    # Keep API import-safe when DB credentials are missing/incorrect.
    conn = None
    cursor = None