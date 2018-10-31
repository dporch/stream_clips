import json
import boto3
import requests


def handler(event, context):
    client_id = '6sugaldogiglso2ddyovsl9cmsda67'
    top_games_url = 'https://api.twitch.tv/helix/games/top'
    client = boto3.client('sqs')
    game_queue_url = 'https://sqs.us-west-2.amazonaws.com/422371343929/games_to_process'
    queue_errors = []
    num_of_games = 0

    headers = {'Client-ID': client_id}
    params = {'first': 100}  # Actually 98

    res = requests.get(url=top_games_url, params=params, headers=headers)
    if not res.ok:
        return {
            "status_code": res.status_code,
            "reason": "Failed to retrieve top 100 games",
            "request_body": res.text
        }
    num_of_games = len(res.json()['data'])

    # Do SQS submission, 1 item per game
    def send_sqs_message(game, delay_seconds):
        response = client.send_message(
            QueueUrl=game_queue_url,
            MessageBody=json.dumps({'id': game['id'], 'name': game['name']}),
            DelaySeconds=delay_seconds  # Intentionally slow down process speed
            #  to dodge twitch rate limit
        )
        return response

    def retry_send_sqs_message(game, delay_seconds, num_tries=5):
        for _ in range(5):
            res = send_sqs_message(game, delay_seconds)
            if not 'errorMessage' in res:
                return True, res
            num_tries += num_tries

        # If fails
        return False, res

    for i, game in enumerate(res.json()['data']):
        success, res = retry_send_sqs_message(game=game, delay_seconds=i)
        if not success:
            queue_errors.append(response)

    return {
        "is_errors": True if len(queue_errors) > 0 else False,
        "errors": queue_errors,
        "num_of_games": num_of_games
    }