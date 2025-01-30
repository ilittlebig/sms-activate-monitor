#
#
# Author: Elias Sjödin
# Created: 2025-01-30

import os
import subprocess
import json
import requests
from dotenv import load_dotenv

load_dotenv()

def get_terraform_output():
    try:
        infra_path = os.path.join(os.path.dirname(__file__), "../infra")
        result = subprocess.run(["terraform", "output", "-json"], capture_output=True, text=True, cwd=infra_path)
        result.check_returncode()
        outputs = json.loads(result.stdout)

        api_gateway_url = outputs.get("api_gateway_url", {}).get("value")
        return api_gateway_url
    except Exception as e:
        print(f"Error fetching Terraform output: {e}")
        exit(1)

def register_commands(discord_token, application_id, api_url):
    url = f"https://discord.com/api/v10/applications/{application_id}/commands"
    headers = {
        "Authorization": f"Bot {discord_token}",
        "Content-Type": "application/json"
    }

    commands = [
        {
            "name": "monitor",
            "description": "Set the country to monitor",
            "options": [
                {
                    "type": 3,
                    "name": "country",
                    "description": "The country to monitor",
                    "required": True
                }
            ]
        },
        {
            "name": "setchannel",
            "description": "Set the alert channel",
            "options": [
                {
                    "type": 7,
                    "name": "channel",
                    "description": "The channel for sending alerts",
                    "required": True
                }
            ]
        },
        {
            "name": "setthreshold",
            "description": "Set the minimum stock increase needed before an alert is sent",
            "options": [
                {
                    "type": 4,
                    "name": "threshold",
                    "description": "Minimum stock increase required for alert",
                    "required": True
                }
            ]
        }
    ]

    for command in commands:
        response = requests.post(url, headers=headers, json=command)
        response.raise_for_status()
        print(f"Registered command: {command['name']}")

if __name__ == "__main__":
    DISCORD_TOKEN = os.getenv("DISCORD_TOKEN");
    APPLICATION_ID = os.getenv("DISCORD_APPLICATION_ID");

    api_gateway_url = get_terraform_output()
    print(api_gateway_url)
    if not api_gateway_url:
        print("API Gateway URL not found. Ensure Terraform outputs are set up correctly.")
        exit(1)

    register_commands(DISCORD_TOKEN, APPLICATION_ID, api_gateway_url)
