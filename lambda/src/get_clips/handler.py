import boto3
import requests
import json


def handler(event, context):
    client = boto3.client('secretsmanager')

    def get_twitch_secret(key):
        res = client.get_secret_value(
            SecretId='TWITCHCREDENTIALS'
        )
        res = json.loads(res)
        return res[key]
# returns our streamclips credentials, host, port, and other info to connect to
# our postgres instance
    def get_postgres_secret():
        res = client.get_secret_value(
            SecretId='streamclips/postgres/lambda-user'
        )
        res = json.loads(res)
        return res

    client_id = get_twitch_secret('TWITCH_CLIENT_ID')
    postgres_config = get_postgres_secret()
    clip_get_url = 'https://api.twitch.tv/helix/clips'
    headers = {'Client-ID': client_id}
    params = {'first': 100, 'game_id': event['id']}  # Actually 98

    res = requests.get(url=clip_get_url, params=params, headers=headers)

    if not res.ok:
        return {
            "status_code": res.status_code,
            "reason": "Failed to retrieve top 100 games",
            "request_body": res.text
        }
        
    # Add clip to database

    conn = psycopg2.connect(
        host = postgres_config['host'], 
        dbname = postgres_config['dbname'], 
        user = postgres_config['username'],
        password = postgres_config['password']
        )

    return {
        "is_errors": True if res.ok else False,
        "body": res.json()
    }
