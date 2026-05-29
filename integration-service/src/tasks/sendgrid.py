from app import celery_app
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import os

@celery_app.task(bind=True, max_retries=3)
def send_email(self, to_email, subject, body):
    message = Mail(
        from_email=os.environ.get('SENDGRID_FROM_EMAIL'),
        to_emails=to_email,
        subject=subject,
        plain_text_content=body
    )
    try:
        sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
        response = sg.send(message)
        return response.status_code
    except Exception as e:
        self.retry(exc=e, countdown=60)
