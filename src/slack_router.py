from logging import getLogger

from fastapi import APIRouter, HTTPException, Request

from .slack_integration import slack_integration
from .slack_security import slack_security

logger = getLogger(__name__)

slack_router = APIRouter()


@slack_router.post("/slack/events")
async def slack_events(request: Request):
    """Handle Slack event subscriptions"""
    try:
        # Get raw body for signature verification
        raw_body = await request.body()

        # Verify the request is from Slack (recommended for production)
        timestamp = request.headers.get("X-Slack-Request-Timestamp", "")
        signature = request.headers.get("X-Slack-Signature", "")

        if not slack_security.verify_slack_request(raw_body, timestamp, signature):
            raise HTTPException(status_code=401, detail="Unauthorized")

        # Parse JSON body
        import json

        body = json.loads(raw_body.decode("utf-8"))

        result = await slack_integration.handle_slack_event(body)
        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error handling Slack event: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
