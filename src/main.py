"""
Created on

@author: Hari

source:

"""

from fastapi import FastAPI, Request
import uvicorn
import time
from fastapi.middleware.cors import CORSMiddleware


import logging

logger = logging.getLogger(__name__)

app = FastAPI(title="RAG Chat API", version="1.0.0")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()

    # Log request
    logger.info(
        f"Request: {request.method} {request.url} "
        f"from {request.client.host if request.client else 'Unknown'}"
    )

    response = await call_next(request)

    # Log response
    process_time = time.time() - start_time
    logger.info(
        f"Response: {request.method} {request.url} "
        f"Status: {response.status_code} "
        f"Time: {process_time:.4f}s"
    )

    return response


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(
        f"Unhandled exception in {request.method} {request.url}: {exc}", exc_info=True
    )
    return {"error": "Internal server error"}, 500


@app.get("/")
async def read_root():
    return {"Hello": "World"}


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
