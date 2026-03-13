from pydantic import BaseModel
from typing import Optional


class LoginRequest(BaseModel):
    email: str
    password: str

class RegisterRequest(BaseModel):
    name: str
    email: str
    password: str
    role: str  # 'student' or 'teacher'


class TopicCreate(BaseModel):
    title: str
    description: Optional[str] = ""
    keywords: str = ""
    teacher_id: int


class EssaySubmission(BaseModel):
    student_id: int
    topic_id: int
    essay_text: str