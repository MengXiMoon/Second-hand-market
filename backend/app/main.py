from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.api import api_router
from app.db.session import engine, Base
import os
from dotenv import load_dotenv

load_dotenv()

# Create database tables automatically
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Second-hand Market API",
    description="Backend API for the second-hand market system (Python + FastAPI)",
    version="1.0.0",
)

# CORS configuration to allow Vue frontend to communicate with the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Router
app.include_router(api_router, prefix="/v1")

@app.get("/")
def root():
    return {"message": "Welcome to the Second-hand Market API. Go to /docs for API documentation."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
