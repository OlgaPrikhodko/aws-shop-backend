import json
import os
import traceback
import uuid

import boto3

from botocore.exceptions import ClientError

# Common headers:
HEADERS = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'POST',
    'Access-Control-Allow-Credentials': True,
    'Content-Type': 'application/json'
}


def handler(event, _context):
    """
    Lambda handler for POST /products endpoint.
    """
    print("POST /products request received")

    try:
        body = json.loads(event["body"])

        validate_product_data(body)
        print("Request body validation successful")

        # Create product using transacton
        new_product = create_product_transaction(body)

        return {
            'statusCode': 201,
            'headers': HEADERS,
            'body': json.dumps(new_product)
        }
    except ValueError as e:
        return error_response(400, str(e))

    except ClientError as e:
        print(f"DynamoDB error: {json.dumps(e.response, indent=2)}")
        return error_response(500, "Database error: " + e.response['Error'].get('Message', 'Unknown error'))

    except Exception as e:
        print(f"Unhandled server error: {str(e)}")
        print(traceback.format_exc())  # Log full traceback
        return error_response(500, "Internal server error")


def create_product_transaction(data):
    """
    Creates a new product and its stock information using a DynamoDB transaction.
    Ensures atomicity: if stock creation fails, product is not created.
    """
    # Initialize DynamoDB resources
    dynamodb = boto3.resource("dynamodb", region_name=os.getenv("AWS_REGION"))
    dynamodb_client = boto3.client('dynamodb')

    product_table_name = os.getenv("PRODUCTS_TABLE_NAME")
    stock_table_name = os.getenv("STOCK_TABLE_NAME")

    if not product_table_name or not stock_table_name:
        raise ValueError(
            "Missing environment variables: PRODUCTS_TABLE_NAME or STOCK_TABLE_NAME")

    # Generate a unique product ID
    product_id = str(uuid.uuid4())

    title = data.get('title')
    description = data.get('description', '')
    price = data.get('price')
    count = data.get('count')

    transaction_items = [
        {
            'Put': {
                'TableName': product_table_name,
                'Item': {
                    'id': {'S': product_id},
                    'title': {'S': title},
                    'description': {'S': description},
                    'price': {'N': str(price)}
                }
            }
        },
        {
            'Put': {
                'TableName': stock_table_name,
                'Item': {
                    'product_id': {'S': product_id},
                    'count': {'N': str(count)}
                }
            }
        }
    ]

    try:
        response = dynamodb_client.transact_write_items(
            TransactItems=transaction_items)
        print(f"Transaction successful: {response}")

        return {
            "message": "Product and stock created successfully",
            "product": {
                "id": product_id,
                "title": data["title"],
                "description": data["description"],
                "price": data["price"],
                "count": data["count"]
            }
        }

    except ClientError as e:
        if e.response['Error']['Code'] == 'TransactionCanceledException':
            raise ValueError(
                "Transaction failed: Potential stock constraint violation.")
        raise

    except Exception as e:
        print(f"Unexpected error type: {type(e)}")
        print(f"Error message: {str(e)}")
        print(f"Full traceback: {traceback.format_exc()}")
        raise


def validate_product_data(data):
    """
    Validates the incoming product data.
    Raises ValueError if validation fails.
    """
    required_fields = {'title': str, 'description': str,
                       'price': (int, float), 'count': int}

    for field, expected_type in required_fields.items():
        if field not in data:
            raise ValueError(f"Missing required field: {field}")
        if not isinstance(data[field], expected_type):
            raise ValueError(
                f"Field '{field}' must be of type {expected_type.__name__}")

    if data['price'] < 0:
        raise ValueError("Price must be a non-negative number")

    if data['count'] < 0:
        raise ValueError("Stock count cannot be negative")


def error_response(status_code, message):
    """
    Helper function to create error responses.
    """
    return {
        'statusCode': status_code,
        'headers': HEADERS,
        'body': json.dumps({'error': message})
    }
