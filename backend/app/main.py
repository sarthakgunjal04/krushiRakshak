from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import Base, engine
from . import fusion_engine, auth

# Create database tables
Base.metadata.create_all(bind=engine)

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
# 🔌 Include routers
# -------------------------------------------------------------------
app.include_router(auth.router, prefix="/auth", tags=["auth"])
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
