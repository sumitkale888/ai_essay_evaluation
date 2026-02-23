from pydantic import BaseModel

class LoginRequest(BaseModel):
    email: str
    password: str

class TopicCreate(BaseModel):
    title: str
    description: str = ""

class EssaySubmission(BaseModel):
    student_id: int
    topic_id: int
    essay_text: str