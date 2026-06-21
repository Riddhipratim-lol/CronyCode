import os
import uvicorn
from fastapi import FastAPI
from src.api.routes import router as api_router

app = FastAPI(
    title="DSA Solver MVP API",
    description="A simplified MVP of the autonomous DSA-solving system's reasoning pipeline.",
    version="0.1.0"
)

# Include the solving and health routes
app.include_router(api_router, prefix="/api")

@app.get("/")
def read_root():
    """Root endpoint welcoming users and pointing to the solve route."""
    return {
        "message": "Welcome to the DSA Solver MVP API.",
        "solve_endpoint": "POST /api/solve",
        "docs_endpoint": "/docs"
    }

if __name__ == "__main__":
    # Run uvicorn server on port 8000 when main.py is executed
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("src.main:app", host="0.0.0.0", port=port, reload=False)
