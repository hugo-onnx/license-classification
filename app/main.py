from fastapi import FastAPI
from app.api import routes
from app.config.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Software License Classification API using Groq LLM"
)

app.include_router(routes.router)

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "endpoints": {
            "POST /api/v1/classify": "Upload CSV file to classify licenses",
            "GET /api/v1/results": "View all classification results",
            "GET /api/v1/results/{license_name}": "View specific license classification",
            "PUT /api/v1/results/{license_name}": "Update a license classification",
            "DELETE /api/v1/results/{license_name}": "Delete a classification",
            "GET /api/v1/stats": "View classification statistics"
        },
        "docs": "/docs",
        "redoc": "/redoc"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )