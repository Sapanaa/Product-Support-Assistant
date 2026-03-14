from fastapi import FastAPI
from app.api.routes import router

app = FastAPI(
    title="Product Support Assitant",
    description="AI support agent for retail product catalog queries.",
    version="1.0.0",
)

app.include_router(router)
