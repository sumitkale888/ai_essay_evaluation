import mysql.connector
import os
from dotenv import load_dotenv


BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
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


def initialize_database():
    """Create classroom-related tables and columns if they are missing."""
    db = get_db_connection()
    cursor = db.cursor()
    try:
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS Classrooms (
                classroom_id INT AUTO_INCREMENT PRIMARY KEY,
                teacher_id INT NOT NULL,
                classroom_name VARCHAR(255) NOT NULL,
                subject_name VARCHAR(255) NOT NULL,
                join_code VARCHAR(16) NOT NULL UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_classrooms_teacher_id (teacher_id),
                INDEX idx_classrooms_join_code (join_code)
            )
            """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS ClassroomMembers (
                classroom_id INT NOT NULL,
                student_id INT NOT NULL,
                joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (classroom_id, student_id),
                INDEX idx_members_student_id (student_id)
            )
            """
        )

        cursor.execute(
            """
            SELECT COUNT(*)
            FROM information_schema.COLUMNS
            WHERE TABLE_SCHEMA = DATABASE()
              AND TABLE_NAME = 'Topics'
              AND COLUMN_NAME = 'classroom_id'
            """
        )
        has_classroom_column = cursor.fetchone()[0] > 0

        if not has_classroom_column:
            cursor.execute("ALTER TABLE Topics ADD COLUMN classroom_id INT NULL")
            cursor.execute("CREATE INDEX idx_topics_classroom_id ON Topics(classroom_id)")

        db.commit()
    finally:
        db.close()