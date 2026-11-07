
from fastapi import FastAPI

from app.api.routes import router

app = FastAPI(
    title="CodebaseGPT",
    description="AI-powered GitHub repository assistant",
    version="1.0.0"
)

# Register API routes
app.include_router(router, prefix="/api")


@app.get("/")
def home():
    return {
        "message": "Welcome to CodebaseGPT!",
        "status": "Backend is running"
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}
