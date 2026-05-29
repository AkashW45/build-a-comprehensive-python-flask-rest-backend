from app import celery_app
import requests
import os

@celery_app.task(bind=True, max_retries=3)
def sync_payroll(self, payroll_run_id):
    adp_api_url = os.environ.get('ADP_API_URL')
    # Placeholder: call ADP API
    return {'status': 'synced'}
