#
#
# Author: Elias Sjödin
# Created: 2025-01-29

import logging
import requests
from utils.sms_activate import check_gmx_stock
from utils.aws import update_guild_config

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def send_to_discord(token, channel_id, gmx_stock, country_name):
    url = f"https://discord.com/api/v10/channels/{channel_id}/messages"
    headers = {
        "Authorization": f"Bot {token}",
        "Content-Type": "application/json"
    }

    branding_url = "https://i.imgur.com/voizd7u.jpeg"
    embed = {
        "color": 0x00ff00,
        "thumbnail": {
            "url": branding_url,
        },
        "fields": [
            {"name": "📦 Stock", "value": gmx_stock, "inline": True},
            {"name": "🌍 Country", "value": country_name, "inline": True},
            {"name": "💻 Provider", "value": "SMSActivate", "inline": False}
        ],
        "footer": {
            "text": "Stay ahead! Monitor by Jaafar",
        }
    }

    message = f"📢 GMX Numbers Available! Stock: **{gmx_stock}**"
    payload = {
        "content": message,
        "embeds": [embed]
    }

    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    return response.status_code


def process_guild(guild, sms_api_key, discord_token):
    channel_id = guild["ChannelID"]
    guild_id = guild["GuildID"]
    country = guild["Country"]

    current_stock = check_gmx_stock(sms_api_key, 43)

    last_stock = guild.get("LastStock", 0)
    threshold = guild.get("Threshold", 50)

    if (current_stock - last_stock) >= threshold:
        send_to_discord(discord_token, channel_id, current_stock, country)
        update_guild_config(guild_id, last_stock=current_stock)
    update_guild_config(guild_id, last_stock=current_stock)
