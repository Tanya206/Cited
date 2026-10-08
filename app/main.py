"""Cited FastAPI application."""

from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI

from app.api.routes import load_services, router


@asynccontextmanager
async def lifespan(app: FastAPI):
    load_dotenv()
    app.state.services = load_services()
    yield


app = FastAPI(title="Cited", version="0.1.0", lifespan=lifespan)
app.include_router(router)
