from app import celery_app
import boto3
import os

@celery_app.task(bind=True, max_retries=3)
def upload_to_s3(self, file_data, key):
    s3 = boto3.client('s3',
                      aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
                      aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'))
    bucket = os.environ.get('S3_BUCKET')
    try:
        s3.put_object(Bucket=bucket, Key=key, Body=file_data)
        return f"s3://{bucket}/{key}"
    except Exception as e:
        self.retry(exc=e, countdown=60)
