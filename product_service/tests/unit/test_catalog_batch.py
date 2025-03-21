import json
from unittest.mock import patch, MagicMock, call
import pytest


@pytest.fixture
def mock_env_vars(monkeypatch):
    monkeypatch.setenv('STOCK_TABLE_NAME', 'test-stock')
    monkeypatch.setenv('PRODUCTS_TABLE_NAME', 'test-products')
    monkeypatch.setenv('SNS_TOPIC_ARN', 'test:arn:sns:topic')
    monkeypatch.setenv('AWS_REGION', 'eu-west-1')


@pytest.fixture
def mock_aws_clients():
    # Create mock clients
    mock_dynamodb_client = MagicMock()
    mock_sns_client = MagicMock()

    # Configure mock responses
    mock_dynamodb_client.transact_write_items.return_value = {}
    mock_sns_client.publish.return_value = {'MessageId': 'test-message-id'}

    # Create the patch
    with patch('product_service.lambda_func.catalog_batch.dynamodb_client', mock_dynamodb_client), \
            patch('product_service.lambda_func.catalog_batch.sns_client', mock_sns_client):

        yield {
            'dynamodb_client': mock_dynamodb_client,
            'sns_client': mock_sns_client
        }


@pytest.fixture
def valid_event():
    return {
        'Records': [{
            'body': json.dumps({
                'id': 'test-id',
                'title': 'Test Product',
                'description': 'Test Description',
                'price': 100,
                'count': 5
            })
        }]
    }


def test_successful_processing(mock_env_vars, valid_event, mock_aws_clients):
    from product_service.lambda_func.catalog_batch import handler

    # Execute lambda handler
    response = handler(valid_event, None)

    # Verify response
    assert response['statusCode'] == 200
    assert json.loads(response['body'])[
        'message'] == 'Products added successfully'

    # Verify DynamoDB transaction
    mock_aws_clients['dynamodb_client'].transact_write_items.assert_called_once_with(
        TransactItems=[
            {
                'Put': {
                    'TableName': 'test-products',
                    'Item': {
                        'id': {'S': 'test-id'},
                        'title': {'S': 'Test Product'},
                        'description': {'S': 'Test Description'},
                        'price': {'N': '100'}
                    }
                }
            },
            {
                'Put': {
                    'TableName': 'test-stock',
                    'Item': {
                        'product_id': {'S': 'test-id'},
                        'count': {'N': '5'}
                    }
                }
            }
        ]
    )

    # Verify SNS notification
    mock_aws_clients['sns_client'].publish.assert_called_once()
    call_kwargs = mock_aws_clients['sns_client'].publish.call_args[1]
    assert call_kwargs['TopicArn'] == 'test:arn:sns:topic'
    assert 'MessageStructure' in call_kwargs
    assert call_kwargs['MessageStructure'] == 'json'

    # Verify SNS message content
    message_content = json.loads(call_kwargs['Message'])
    assert 'default' in message_content
    default_content = json.loads(message_content['default'])
    assert default_content['message'] == 'New product added'
    assert len(default_content['products']) == 1
    assert default_content['products'][0]['id'] == 'test-id'


def test_missing_required_field(mock_env_vars, mock_aws_clients):
    from product_service.lambda_func.catalog_batch import handler

    # Create event with missing field
    event = {
        'Records': [{
            'body': json.dumps({
                'id': 'test-id',
                'title': 'Test Product',
                # missing description
                'price': 100,
                'count': 5
            })
        }]
    }

    # Execute lambda handler
    response = handler(event, None)

    # Verify response
    assert response['statusCode'] == 400
    assert 'description is missing' in json.loads(response['body'])['message']

    # Verify no DynamoDB or SNS calls were made
    mock_aws_clients['dynamodb_client'].transact_write_items.assert_not_called()
    mock_aws_clients['sns_client'].publish.assert_not_called()


def test_multiple_records(mock_env_vars, mock_aws_clients):
    from product_service.lambda_func.catalog_batch import handler

    event = {
        'Records': [
            {
                'body': json.dumps({
                    'id': 'test-id-1',
                    'title': 'Test Product 1',
                    'description': 'Test Description 1',
                    'price': 100,
                    'count': 5
                })
            },
            {
                'body': json.dumps({
                    'id': 'test-id-2',
                    'title': 'Test Product 2',
                    'description': 'Test Description 2',
                    'price': 200,
                    'count': 10
                })
            }
        ]
    }

    # Execute lambda handler
    response = handler(event, None)

    # Debug prints
    print("\nResponse:", response)
    print("\nDynamoDB calls:")
    print(mock_aws_clients['dynamodb_client'].transact_write_items.mock_calls)
    print("\nSNS calls:")
    print(mock_aws_clients['sns_client'].publish.mock_calls)

    # Verify response
    assert response['statusCode'] == 200
    assert json.loads(response['body'])[
        'message'] == 'Products added successfully'

    # Verify DynamoDB transactions
    expected_calls = [
        call(TransactItems=[
            {
                'Put': {
                    'TableName': 'test-products',
                    'Item': {
                        'id': {'S': 'test-id-1'},
                        'title': {'S': 'Test Product 1'},
                        'description': {'S': 'Test Description 1'},
                        'price': {'N': '100'}
                    }
                }
            },
            {
                'Put': {
                    'TableName': 'test-stock',
                    'Item': {
                        'product_id': {'S': 'test-id-1'},
                        'count': {'N': '5'}
                    }
                }
            }
        ]),
        call(TransactItems=[
            {
                'Put': {
                    'TableName': 'test-products',
                    'Item': {
                        'id': {'S': 'test-id-2'},
                        'title': {'S': 'Test Product 2'},
                        'description': {'S': 'Test Description 2'},
                        'price': {'N': '200'}
                    }
                }
            },
            {
                'Put': {
                    'TableName': 'test-stock',
                    'Item': {
                        'product_id': {'S': 'test-id-2'},
                        'count': {'N': '10'}
                    }
                }
            }
        ])
    ]

    # Verify DynamoDB calls
    assert mock_aws_clients['dynamodb_client'].transact_write_items.call_count == 2
    mock_aws_clients['dynamodb_client'].transact_write_items.assert_has_calls(
        expected_calls, any_order=True)

    # Verify SNS notification
    mock_aws_clients['sns_client'].publish.assert_called_once()
    call_kwargs = mock_aws_clients['sns_client'].publish.call_args[1]

    # Verify SNS message content
    message_content = json.loads(call_kwargs['Message'])
    default_content = json.loads(message_content['default'])
    assert len(default_content['products']) == 2
    assert default_content['products'][0]['id'] == 'test-id-1'
    assert default_content['products'][1]['id'] == 'test-id-2'
