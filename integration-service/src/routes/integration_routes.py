from flask import Blueprint, request, jsonify
from app import celery_app
from src.tasks.slack import send_slack_notification
from src.tasks.sendgrid import send_email
from src.tasks.s3 import upload_to_s3
from src.tasks.stripe import process_stripe_payment
from src.tasks.adp import sync_payroll

integration_bp = Blueprint('integrations', __name__)

@integration_bp.route('/slack/notify', methods=['POST'])
def trigger_slack_notification():
    data = request.get_json()
    task = send_slack_notification.delay(data['message'], data.get('channel', '#general'))
    return jsonify({'task_id': task.id}), 202

@integration_bp.route('/email/send', methods=['POST'])
def trigger_email():
    data = request.get_json()
    task = send_email.delay(data['to'], data['subject'], data['body'])
    return jsonify({'task_id': task.id}), 202

@integration_bp.route('/s3/upload', methods=['POST'])
def trigger_s3_upload():
    # Expect file in request, handled as task
    task = upload_to_s3.delay(request.files)
    return jsonify({'task_id': task.id}), 202

@integration_bp.route('/stripe/enroll', methods=['POST'])
def trigger_stripe_enrollment():
    data = request.get_json()
    task = process_stripe_payment.delay(data['plan'], data['user_id'])
    return jsonify({'task_id': task.id}), 202

@integration_bp.route('/adp/sync', methods=['POST'])
def trigger_adp_sync():
    data = request.get_json()
    task = sync_payroll.delay(data['payroll_run_id'])
    return jsonify({'task_id': task.id}), 202
