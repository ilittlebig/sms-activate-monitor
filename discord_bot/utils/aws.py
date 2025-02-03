#
#
# Author: Elias Sjödin
# Created: 2025-01-29

import boto3
import json
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb = boto3.client("dynamodb")

ADMINISTRATOR_PERMISSION = 0x00000008

def check_permissions(permissions):
    if permissions & ADMINISTRATOR_PERMISSION:
        return None

    return {
        "type": 4,
        "data": {
            "content": "You do not have the required permissions to use this command.",
            "flags": 64
        }
    }


def get_secrets(secret_arn):
    client = boto3.client("secretsmanager")
    try:
        response = client.get_secret_value(SecretId=secret_arn)
        secret_string = response.get("SecretString")
        if secret_string:
            return json.loads(secret_string)
        else:
            raise ValueError("SecretString is empty or unavailable in the response.")
    except Exception as e:
        raise Exception(f"Failed to fetch secrets: {e}")


def get_guild_config(guild_id):
    response = dynamodb.get_item(
        TableName="DiscordMonitoringConfig",
        Key={"GuildID": {"S": guild_id}}
    )

    if "Item" in response:
        return {
            "GuildID": item["GuildID"]["S"],
            "ChannelID": response["Item"]["ChannelID"]["S"],
            "Country": response["Item"]["Country"]["S"],
            "LastStock": int(item.get("LastStock", {}).get("N", 0)),
            "Threshold": int(item.get("Threshold", {}).get("N", 50)),
        }
    return None


def get_all_guilds():
    try:
        response = dynamodb.scan(TableName="DiscordMonitoringConfig")
        guilds = [
            {
                "GuildID": item["GuildID"]["S"],
                "ChannelID": item["ChannelID"]["S"],
                "Country": item["Country"]["S"],
                "LastStock": int(item.get("LastStock", {}).get("N", 0)),
                "Threshold": int(item.get("Threshold", {}).get("N", 50)),
            }
            for item in response.get("Items", [])
        ]
        return guilds
    except Exception as e:
        logger.error(f"Error fetching all guilds: {e}")
        return []


def update_guild_config(guild_id, last_stock=None, threshold=None):
    update_expressions = []
    expression_values = {}

    if last_stock is not None:
        update_expressions.append("LastStock = :lastStock")
        expression_values[":lastStock"] = {"N": str(last_stock)}

    if threshold is not None:
        update_expressions.append("Threshold = :threshold")
        expression_values[":threshold"] = {"N": str(threshold)}

    if not update_expressions:
        return
    update_expression = "SET " + ", ".join(update_expressions)

    try:
        dynamodb.update_item(
            TableName="DiscordMonitoringConfig",
            Key={"GuildID": {"S": guild_id}},
            UpdateExpression=update_expression,
            ExpressionAttributeValues=expression_values
        )
        logger.info(f"Updated guild {guild_id} with {update_expressions}")
    except Exception as e:
        logger.error(f"Error updating guild config: {e}")


def process_command(body):
    logger.info(f"Processing command: {body}")

    data = body.get("data")
    if not data:
        logger.error("No 'data' key found in body")
        return {"statusCode": 400, "body": "Invalid body structure"}

    command_name = data.get("name")
    if not command_name:
        logger.error("No 'name' key found in 'data'")
        return {"statusCode": 400, "body": "Missing command name"}

    guild_id = body.get("guild_id")
    member = body.get("member", {})

    user_id = member.get("user", {}).get("id")
    is_owner = body.get("guild", {}).get("owner_id") == user_id
    permissions = int(member.get("permissions", 0))

    not_allowed_payload = check_permissions(permissions)
    if not is_owner and not_allowed_payload:
        return not_allowed_payload

    if command_name == "monitor":
        country = body["data"]["options"][0]["value"]
        dynamodb.update_item(
            TableName="DiscordMonitoringConfig",
            Key={"GuildID": {"S": guild_id}},
            UpdateExpression="SET Country = :country",
            ExpressionAttributeValues={":country": {"S": country}}
        )

        return {
            "type": 4,
            "data": { "content": f"Monitoring country set to {country}." }
        }

    elif command_name == "setchannel":
        channel_id = body["data"]["options"][0]["value"]
        dynamodb.update_item(
            TableName="DiscordMonitoringConfig",
            Key={"GuildID": {"S": guild_id}},
            UpdateExpression="SET ChannelID = :channel",
            ExpressionAttributeValues={":channel": {"S": channel_id}}
        )

        return {
            "type": 4,
            "data": { "content": f"Alerts will be sent to <#{channel_id}>." }
        }

    elif command_name == "setthreshold":
        threshold_value = body["data"]["options"][0]["value"]
        # TODO: Validate it's a positive integer or something
        update_guild_config(guild_id, threshold=threshold_value)
        return {
            "type": 4,
            "data": { "content": f"Threshold updated to {threshold_value}." }
        }
