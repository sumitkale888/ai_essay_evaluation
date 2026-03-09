from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import auth, teacher, student

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include separate route files
app.include_router(auth.router, tags=["Authentication"]) # No prefix for login/register usually
app.include_router(teacher.router, prefix="/teacher", tags=["Teacher Actions"])

app.include_router(student.router, prefix="/student", tags=["Student Actions"])

@app.get("/")
def home():
    return {"message": "AI Essay Grader API is Running"}