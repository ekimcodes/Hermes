from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Grid Outage Prediction & ETR Model",
    description="API for predicting power grid outages and estimating restoration times.",
    version="1.0.0"
)

# CORS Configuration
origins = ["*"]  # For development; restrict in production

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Grid Outage Prediction API is running"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

from .api.api import api_router
app.include_router(api_router, prefix="/api/v1")

