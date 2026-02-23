import mysql.connector
import os
from dotenv import load_dotenv

# Accurately locate the .env file
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV_PATH = os.path.join(BASE_DIR, ".env")

load_dotenv(dotenv_path=ENV_PATH)

def get_db_connection():
    db_host = os.getenv("DB_HOST", "127.0.0.1")
    db_user = os.getenv("DB_USER", "root")
    db_password = os.getenv("DB_PASSWORD")
    db_name = os.getenv("DB_NAME", "ai_essay_grader")

    if not db_password:
        raise ValueError(f"Password not found. Please check your .env file at: {ENV_PATH}")

    return mysql.connector.connect(
        host=db_host,
        user=db_user,
        password=db_password,
        database=db_name
    )