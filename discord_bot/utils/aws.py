#
#
# Author: Elias Sjödin
# Created: 2025-01-29

import boto3
import json

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
