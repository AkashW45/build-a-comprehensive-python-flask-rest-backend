from app import celery_app
import stripe
import os

@celery_app.task(bind=True, max_retries=3)
def process_stripe_payment(self, plan_id, user_id):
    stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')
    try:
        # Create or update subscription
        # Placeholder
        return {'status': 'success'}
    except Exception as e:
        self.retry(exc=e, countdown=60)
