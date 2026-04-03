from pydantic import BaseModel
from typing import Optional, List


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


class PlagiarismResult(BaseModel):
    plagiarism_percentage: float
    plagiarism_level: str
    feedback: str
    comparison_count: int
    detailed_comparisons: Optional[List[dict]] = None


class EvaluationResult(BaseModel):
    score: float
    plagiarism: float
    plagiarism_level: str
    feedback: str
    plagiarism_feedback: str
    word_count: int
    is_plagiarized: bool