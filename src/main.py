import os
from contextlib import asynccontextmanager
from logging import getLogger

from fastapi import FastAPI, Request, Response
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

from .server.error import init_error_handlers
from .server.middleware import init_middleware
from .slack_router import slack_router

logger = getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Server running on port {os.getenv('BL_SERVER_PORT', 80)}")
    yield
    logger.info("Server shutting down")


app = FastAPI(lifespan=lifespan)
init_error_handlers(app)
init_middleware(app)
app.include_router(slack_router)


@app.post("/")
async def root(request: Request):
    return Response(
        content="This template is designed to work with Slack.\nFor setup and usage instructions, please see: https://github.com/blaxel-templates/template-slack-chatbot/blob/main/docs/SLACK_SETUP.md",
        status_code=200,
        media_type="text/plain",
    )


FastAPIInstrumentor.instrument_app(app)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=80)
