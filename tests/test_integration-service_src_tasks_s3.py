import pytest
from unittest.mock import patch, MagicMock

from src.tasks.s3 import upload_to_s3


class MockTask:
    def retry(self, exc=None, countdown=None):
        pass


@patch('src.tasks.s3.boto3.client')
@patch.dict('src.tasks.s3.os.environ', {'AWS_ACCESS_KEY_ID': 'test_key', 'AWS_SECRET_ACCESS_KEY': 'test_secret', 'S3_BUCKET': 'test_bucket'}, clear=True)
def test_upload_to_s3_success(mock_boto_client):
    mock_s3 = MagicMock()
    mock_boto_client.return_value = mock_s3
    mock_self = MockTask()
    file_data = b"test data"
    key = "test/key.txt"
    result = upload_to_s3(mock_self, file_data, key)
    mock_s3.put_object.assert_called_once_with(Bucket='test_bucket', Key=key, Body=file_data)
    assert result == "s3://test_bucket/test/key.txt"


@patch('src.tasks.s3.boto3.client')
@patch.dict('src.tasks.s3.os.environ', {'AWS_ACCESS_KEY_ID': 'test_key', 'AWS_SECRET_ACCESS_KEY': 'test_secret', 'S3_BUCKET': 'test_bucket'}, clear=True)
def test_upload_to_s3_retries_on_failure(mock_boto_client):
    mock_s3 = MagicMock()
    mock_s3.put_object.side_effect = Exception("S3 error")
    mock_boto_client.return_value = mock_s3
    mock_self = MagicMock()
    upload_to_s3(mock_self, b"data", "key")
    mock_self.retry.assert_called_once_with(exc=Exception("S3 error"), countdown=60)


@patch('src.tasks.s3.boto3.client')
@patch.dict('src.tasks.s3.os.environ', {}, clear=True)
def test_upload_to_s3_missing_bucket_env(mock_boto_client):
    mock_s3 = MagicMock()
    mock_s3.put_object.side_effect = Exception("Invalid bucket")
    mock_boto_client.return_value = mock_s3
    mock_self = MagicMock()
    upload_to_s3(mock_self, b"data", "key")
    mock_boto_client.assert_called_once_with('s3', aws_access_key_id=None, aws_secret_access_key=None)
    mock_self.retry.assert_called_once_with(exc=Exception("Invalid bucket"), countdown=60)


@patch('src.tasks.s3.boto3.client')
@patch.dict('src.tasks.s3.os.environ', {'AWS_ACCESS_KEY_ID': 'custom_key', 'AWS_SECRET_ACCESS_KEY': 'custom_secret', 'S3_BUCKET': 'custom_bucket'}, clear=True)
def test_upload_to_s3_uses_environment_credentials(mock_boto_client):
    mock_s3 = MagicMock()
    mock_boto_client.return_value = mock_s3
    mock_self = MockTask()
    upload_to_s3(mock_self, b"data", "key")
    mock_boto_client.assert_called_once_with('s3', aws_access_key_id='custom_key', aws_secret_access_key='custom_secret')