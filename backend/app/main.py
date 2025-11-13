from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from . import fusion_engine

app = FastAPI(
    title="AgriSense Backend API",
    description="Backend API for AgriSense PWA — Farmer advisory and risk management system",
    version="1.0.0",
)

# -------------------------------------------------------------------
# ✅ Enable CORS (important for frontend-backend communication)
# -------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (you can restrict later)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------------------------------------------
# 🧩 Data Models
# -------------------------------------------------------------------
class SignupModel(BaseModel):
    name: str
    phone: Optional[str] = None
    email: str
    password: str
    userType: str

class LoginModel(BaseModel):
    email: str
    password: str


# -------------------------------------------------------------------
# 🧠 Dummy database (temporary for testing)
# -------------------------------------------------------------------
users_db = {}  # Simple in-memory store


# -------------------------------------------------------------------
# 🚀 Signup Endpoint
# -------------------------------------------------------------------
@app.post("/auth/signup")
async def signup(user: SignupModel):
    # Check if email already exists
    if user.email in users_db:
        raise HTTPException(status_code=409, detail="Email already registered")

    # Save new user (simulating DB insert)
    users_db[user.email] = {
        "name": user.name,
        "phone": user.phone,
        "email": user.email,
        "password": user.password,  # In real app → hash this
        "userType": user.userType,
    }

    # Return token and user data
    return {
        "access_token": "sample.jwt.token",
        "message": f"User {user.name} registered successfully",
        "user": {
            "name": user.name,
            "email": user.email,
            "phone": user.phone,
            "userType": user.userType,
        }
    }


# -------------------------------------------------------------------
# 🔑 Login Endpoint
# -------------------------------------------------------------------
@app.post("/auth/login")
async def login(data: LoginModel):
    # Check if user exists
    user = users_db.get(data.email)
    if not user or user["password"] != data.password:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    # Return token and user data
    return {
        "access_token": "sample.jwt.token",
        "message": f"Welcome back, {user['name']}",
        "user": {
            "name": user["name"],
            "email": user["email"],
            "phone": user.get("phone"),
            "userType": user["userType"],
        }
    }


# -------------------------------------------------------------------
# 👤 Get Current User Profile
# -------------------------------------------------------------------
@app.get("/auth/me")
async def get_current_user():
    # Get token from Authorization header (simplified for now)
    # In production, you'd validate the JWT token properly
    # For now, we'll use a simple approach with email from query or header
    from fastapi import Header
    from typing import Optional
    
    # Simple approach: get user from stored token email mapping
    # In real app, decode JWT token to get email
    return {"message": "Use Authorization header with token"}

# Simplified version - get user by email (for testing)
@app.get("/auth/user")
async def get_user_by_email(email: str):
    user = users_db.get(email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Don't return password
    return {
        "name": user["name"],
        "email": user["email"],
        "phone": user.get("phone"),
        "userType": user["userType"],
    }


# -------------------------------------------------------------------
# 🔌 Include routers
# -------------------------------------------------------------------
app.include_router(fusion_engine.router)

# -------------------------------------------------------------------
# 🌐 Root Route
# -------------------------------------------------------------------
@app.get("/")
def root():
    return {"message": "Welcome to AgriSense Backend API"}


# -------------------------------------------------------------------
# ⚙️ To Run the Server:
# -------------------------------------------------------------------
# Open terminal inside backend folder and run:
# uvicorn main:app --reload
#
# Then visit http://127.0.0.1:8000/docs to test APIs interactively.
