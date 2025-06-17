import logging
import os
from time import time

from asgi_correlation_id import CorrelationIdMiddleware
from fastapi import FastAPI, Request, Response

logger = logging.getLogger(__name__)


def init_middleware(app: FastAPI):
    app.add_middleware(CorrelationIdMiddleware)

    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        start_time = time()

        response: Response = await call_next(request)

        process_time = (time() - start_time) * 1000
        formatted_process_time = "{0:.2f}".format(process_time)
        rid_header = response.headers.get("X-Request-Id")
        request_id = rid_header or response.headers.get("X-Blaxel-Request-Id")
        message = (
            f"{request.method} {request.url.path} {response.status_code} {formatted_process_time}ms rid={request_id}"
        )
        if response.status_code >= 400:
            logger.error(message)
        else:
            logger.info(message)

        return response

    @app.middleware("http")
    async def add_cors_headers(request: Request, call_next):
        app_url = "https://app.blaxel.ai" if os.getenv("BL_ENV") == "prod" else "https://app.blaxel.dev"

        # Handle preflight OPTIONS requests
        if request.method == "OPTIONS":
            response = Response()
            response.headers["Access-Control-Allow-Origin"] = app_url
            response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, PATCH, OPTIONS, HEAD"
            response.headers["Access-Control-Allow-Headers"] = (
                "Content-Type, Authorization, X-Requested-With, Accept, Origin, X-Request-Id, X-Blaxel-Request-Id"
            )
            response.headers["Access-Control-Allow-Credentials"] = "true"
            response.headers["Access-Control-Max-Age"] = "86400"  # 24 hours
            response.headers["Access-Control-Expose-Headers"] = "X-Request-Id, X-Blaxel-Request-Id"
            return response

        response = await call_next(request)

        # Add CORS headers to all responses
        response.headers["Access-Control-Allow-Origin"] = app_url
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, PATCH, OPTIONS, HEAD"
        response.headers["Access-Control-Allow-Headers"] = (
            "Content-Type, Authorization, X-Requested-With, Accept, Origin, X-Request-Id, X-Blaxel-Request-Id"
        )
        response.headers["Access-Control-Allow-Credentials"] = "true"
        response.headers["Access-Control-Max-Age"] = "86400"  # 24 hours
        response.headers["Access-Control-Expose-Headers"] = "X-Request-Id, X-Blaxel-Request-Id"

        return response
