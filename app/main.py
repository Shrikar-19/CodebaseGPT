from fastapi import FastAPI

app = FastAPI(
    title="CodebaseGPT",
    description="AI-powered GitHub repository assistant",
    version="1.0.0"
)


@app.get("/")
def home():
    return {
        "message": "Welcome to CodebaseGPT!",
        "status": "Backend is running"
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}