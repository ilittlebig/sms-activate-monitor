#
#
# Author: Elias Sjödin
# Created: 2025-01-29

import sys
import os
import json
import nacl.signing
import nacl.exceptions
from nacl.signing import VerifyKey

sys.path.append(os.path.join(os.path.dirname(__file__), "vendor"))

import logging
from dotenv import load_dotenv
from utils.discord import send_to_discord, process_guild
from utils.aws import (
    get_secrets, get_guild_config, process_command,
    get_all_guilds
)

logger = logging.getLogger()
logger.setLevel(logging.INFO)

load_dotenv()

PUBLIC_KEY = os.getenv("DISCORD_PUBLIC_KEY")
if not PUBLIC_KEY:
    raise ValueError("DISCORD_PUBLIC_KEY environment variable is required")

def verify_signature(event):
    headers = event.get("headers", {})
    signature = headers.get("x-signature-ed25519") or headers.get("X-Signature-Ed25519")
    timestamp = headers.get("x-signature-timestamp") or headers.get("X-Signature-Timestamp")

    body = event.get("body", "")
    raw_body = event["body"] if isinstance(event["body"], str) else json.dumps(event["body"])

    if not signature or not timestamp:
        logger.error("Missing signature or timestamp")
        return False

    try:
        verify_key = VerifyKey(bytes.fromhex(PUBLIC_KEY))
        verify_key.verify(f"{timestamp}{raw_body}".encode(), bytes.fromhex(signature))
        return True
    except nacl.exceptions.BadSignatureError:
        logger.error("Invalid signature")
        return False


def lambda_handler(event, context):
    logger.info(f"Received event: {event}")

    is_scheduled_event = event.get("source") == "aws.events"
    local_mode = os.getenv("LOCAL_TESTING", "false").lower() == "true"

    if not is_scheduled_event and not local_mode:
        if not verify_signature(event):
            return {"statusCode": 401, "body": "Invalid request signature"}

    body = json.loads(event.get("body", "{}"))
    if body.get("type") == 1: # Type 1 = PING
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"type": 1})
        }

    if body.get("type") == 2: # Type 2 = Slash Command
        command_response = process_command(body)
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps(command_response)
        }

    secrets = {
        "DISCORD_TOKEN": os.getenv("DISCORD_TOKEN"),
        "SMS_ACTIVATE_API_KEY": os.getenv("SMS_ACTIVATE_API_KEY"),
    } if local_mode else get_secrets(os.getenv("SECRETS_ARN"))

    discord_token = secrets["DISCORD_TOKEN"]
    sms_api_key = secrets["SMS_ACTIVATE_API_KEY"]

    if is_scheduled_event:
        for guild in get_all_guilds():
            process_guild(guild, sms_api_key, discord_token)
    else:
        guild_id = event.get("guild_id")
        if guild_id:
            config = get_guild_config(guild_id)
            if config:
                process_guild(config, sms_api_key, discord_token)

    return {"statusCode": 200, "body": "Execution completed"}
