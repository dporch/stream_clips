import boto3
import requests


def handler(event, context):
    event = {"id": "488615", "name": "Street Fighter V"}
    client_id = '6sugaldogiglso2ddyovsl9cmsda67'
    clip_get_url = 'https://api.twitch.tv/helix/clips'
    client = boto3.client('sqs')
    game_queue_url = 'https://sqs.us-west-2.amazonaws.com/422371343929/games_to_process'
    queue_errors = []
    num_of_games = 0

    headers = {'Client-ID': client_id}
    params = {'first': 100, 'game_id': event['id']}  # Actually 98

    res = requests.get(url=clip_get_url, params=params, headers=headers)

    if not res.ok:
        return {
            "status_code": res.status_code,
            "reason": "Failed to retrieve top 100 games",
            "request_body": res.text
        }

    return {
        "is_errors": True if len(queue_errors) > 0 else False,
        "errors": queue_errors,
        "body": res.json()
    }