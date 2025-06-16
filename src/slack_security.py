import hashlib
import hmac
import os
import time
from logging import getLogger

logger = getLogger(__name__)

class SlackSecurity:
    def __init__(self):
        self.signing_secret = os.getenv("SLACK_SIGNING_SECRET")

    def verify_slack_request(self, body: bytes, timestamp: str, signature: str) -> bool:
        """
        Verify that a request came from Slack by validating the signature.

        Args:
            body: Raw request body as bytes
            timestamp: X-Slack-Request-Timestamp header value
            signature: X-Slack-Signature header value

        Returns:
            bool: True if the request is verified, False otherwise
        """
        if not self.signing_secret:
            logger.warning("SLACK_SIGNING_SECRET not configured - skipping signature verification")
            return True  # Allow requests if no secret is configured (development mode)

        try:
            # Check timestamp to prevent replay attacks (should be within 5 minutes)
            current_time = int(time.time())
            request_time = int(timestamp)

            if abs(current_time - request_time) > 300:  # 5 minutes
                logger.warning("Slack request timestamp too old")
                return False

            # Create the signature base string
            sig_basestring = f"v0:{timestamp}:{body.decode('utf-8')}"

            # Calculate the expected signature
            expected_signature = 'v0=' + hmac.new(
                self.signing_secret.encode(),
                sig_basestring.encode(),
                hashlib.sha256
            ).hexdigest()

            # Compare signatures
            if hmac.compare_digest(expected_signature, signature):
                return True
            else:
                logger.warning("Slack request signature verification failed")
                return False

        except Exception as e:
            logger.error(f"Error verifying Slack request: {e}")
            return False

# Global instance
slack_security = SlackSecurity()