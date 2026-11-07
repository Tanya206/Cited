"""Cited FastAPI application."""

from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI

from app.api.routes import load_services, router


@asynccontextmanager
async def lifespan(app: FastAPI): #FASTAPI: Creates the web application; lifespan runs startup and shutdown logic around its lifetime.
    load_dotenv() #loads the local environment variables from a .env file into the application. This is useful for managing configuration settings, such as database credentials or API keys, without hardcoding them into the codebase.
    app.state.services = load_services() #loads Chroma, BM25, the embedding model, and reranker once.
    yield # means the application is now running and ready to handle requests. The code after the yield statement will be executed when the application is shutting down.


app = FastAPI(title="Cited", version="0.1.0", lifespan=lifespan)
app.include_router(router)
