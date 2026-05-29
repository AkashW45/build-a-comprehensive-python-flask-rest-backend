from app import celery_app
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import os

@celery_app.task(bind=True, max_retries=3)
def send_slack_notification(self, message, channel):
    client = WebClient(token=os.environ.get('SLACK_BOT_TOKEN'))
    try:
        response = client.chat_postMessage(channel=channel, text=message)
        return response['ok']
    except SlackApiError as e:
        self.retry(exc=e, countdown=60)
