from fastapi import APIRouter, HTTPException
from ..models import LoginRequest, RegisterRequest
from ..core.database import get_db_connection
from ..core.security import get_password_hash, verify_password

router = APIRouter()

@router.post("/register")
def register(request: RegisterRequest):
    db = get_db_connection()
    cursor = db.cursor()
    try:
        cursor.execute("SELECT user_id FROM Users WHERE email = %s", (request.email,))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="Email already registered")

        hashed_password = get_password_hash(request.password)
        query = "INSERT INTO Users (name, email, password, role) VALUES (%s, %s, %s, %s)"
        values = (request.name, request.email, hashed_password, request.role.lower())
        
        cursor.execute(query, values)
        db.commit()
        return {"message": "User created successfully", "role": request.role.lower()}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()

@router.post("/login")
def login(request: LoginRequest):
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute("SELECT user_id, role, name, password FROM Users WHERE email = %s", (request.email,))
        user = cursor.fetchone()

        if user and verify_password(request.password, user["password"]):
            return {
                "message": "Login successful", 
                "user_id": user["user_id"], 
                "role": user["role"], 
                "name": user["name"]
            }
        raise HTTPException(status_code=401, detail="Invalid email or password")
    finally:
        db.close()