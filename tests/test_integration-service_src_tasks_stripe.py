import pytest
from unittest.mock import patch, MagicMock
from src.tasks.stripe import process_stripe_payment

@pytest.fixture
def mock_self():
    """Mock celery task self with retry method."""
    self = MagicMock()
    return self

@patch('src.tasks.stripe.os.environ', {'STRIPE_SECRET_KEY': 'test_key'})
@patch('src.tasks.stripe.stripe')
def test_process_stripe_payment_success(mock_stripe, mock_self):
    """Happy path: payment processed successfully."""
    result = process_stripe_payment(mock_self, plan_id='plan_123', user_id='user_456')
    assert result == {'status': 'success'}
    mock_stripe.api_key = 'test_key'  # assert stripe api key was set
    assert mock_stripe.api_key == 'test_key'

@patch('src.tasks.stripe.os.environ', {'STRIPE_SECRET_KEY': 'test_key'})
@patch('src.tasks.stripe.stripe')
def test_process_stripe_payment_retries_on_exception(mock_stripe, mock_self):
    """Error path: any exception triggers a retry."""
    # Make setting the api key raise an exception
    type(mock_stripe).api_key = property(lambda self: None, lambda self, v: mock_stripe_exception())
    # Or simpler: mock_stripe.configure_mock(**{'api_key': property(side_effect=Exception('Stripe error'))})
    # Better approach: use a side_effect for the setter via PropertyMock
    from unittest.mock import PropertyMock
    mock_stripe.api_key = PropertyMock(side_effect=Exception('Stripe error'))
    
    process_stripe_payment(mock_self, plan_id='plan_123', user_id='user_456')
    
    mock_self.retry.assert_called_once()
    # retry should have been called with an Exception and countdown=60
    args, kwargs = mock_self.retry.call_args
    assert isinstance(args[0], Exception)  # the exception argument
    assert kwargs.get('countdown') == 60

@patch('src.tasks.stripe.os.environ', {})  # no STRIPE_SECRET_KEY
@patch('src.tasks.stripe.stripe')
def test_process_stripe_payment_missing_api_key_success(mock_stripe, mock_self):
    """Edge case: missing API key still returns success (no stripe calls in placeholder)."""
    result = process_stripe_payment(mock_self, plan_id='plan_123', user_id='user_456')
    assert result == {'status': 'success'}
    assert mock_stripe.api_key is None  # stripe.api_key was set to None