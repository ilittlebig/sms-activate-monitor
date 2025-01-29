#
#
# Author: Elias Sjödin
# Created: 2025-01-29

import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "vendor"))

import logging
from dotenv import load_dotenv
from utils.sms_activate import check_gmx_stock
from utils.discord import send_to_discord
from utils.aws import get_secrets

logger = logging.getLogger()
logger.setLevel(logging.INFO)

load_dotenv()

def lambda_handler(event, context):
    if os.getenv("LOCAL_TESTING", "false").lower() == "true":
        logger.info("Running in local testing mode")
        secrets = {
            "DISCORD_TOKEN": os.getenv("DISCORD_TOKEN"),
            "SMS_ACTIVATE_API_KEY": os.getenv("SMS_ACTIVATE_API_KEY"),
            "CHANNEL_ID": os.getenv("CHANNEL_ID"),
        }
    else:
        logger.info("Running in local production mode")
        secrets_arn = os.getenv("SECRETS_ARN")
        if not secrets_arn:
            raise ValueError("SECRETS_ARN is required in production mode")
        secrets = get_secrets(secrets_arn)

    discord_token = secrets["DISCORD_TOKEN"]
    sms_api_key = secrets["SMS_ACTIVATE_API_KEY"]
    channel_id = secrets["CHANNEL_ID"]

    gmx_stock = check_gmx_stock(sms_api_key)
    logger.info(f"GMX Stock: {gmx_stock}")

    if gmx_stock > 0:
        send_to_discord(discord_token, channel_id, gmx_stock, "Germany")
    else:
        logger.info("No GMX stock available.")

    return {"statusCode": 200, "body": "Execution completed"}
