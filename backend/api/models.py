from pydantic import BaseModel
from typing import Optional

# --- AUTH MODELS ---
class LoginRequest(BaseModel):
    email: str
    password: str

class RegisterRequest(BaseModel):
    name: str
    email: str
    password: str
    role: str  # 'student' or 'teacher'

# --- TEACHER MODELS ---
class TopicCreate(BaseModel):
    title: str
    description: Optional[str] = ""
    keywords: str = ""
    teacher_id: int

# --- STUDENT MODELS ---
class EssaySubmission(BaseModel):
    student_id: int
    topic_id: int
    essay_text: str