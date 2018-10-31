import boto3
import requests
import json


def handler(event, context):
    client = boto3.client('secretsmanager')

    def get_secret(key):
        res = client.get_secret_value(
            SecretId='TWITCHCREDENTIALS'
        )
        res = json.loads(res)
        return res[key]

    client_id = get_secret('TWITCH_CLIENT_ID')
    clip_get_url = 'https://api.twitch.tv/helix/clips'

    headers = {'Client-ID': client_id}
    params = {'first': 100, 'game_id': event['id']}  # Actually 98

    res = requests.get(url=clip_get_url, params=params, headers=headers)

    # Add clip to database

    if not res.ok:
        return {
            "status_code": res.status_code,
            "reason": "Failed to retrieve top 100 games",
            "request_body": res.text
        }

    return {
        "is_errors": True if res.ok else False,
        "body": res.json()
    }