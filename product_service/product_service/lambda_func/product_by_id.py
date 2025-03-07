import json
import os
import boto3


# Common headers for all responses
HEADERS = {
    "Content-Type": "application/json",
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET",
    "Access-Control-Allow-Credentials": True,
}


def handler(event, _context):
    """
    Lambda handler for GET /products/{productId} endpoint.
    Returns a single product with its stock information.
    """
    # Log the event for debugging purposes
    print("GET /products/{{productId}} request received")
    print(f"Event pathParameters: {json.dumps(event.get('pathParameters'))}")

    if not event.get('pathParameters') or 'id' not in event['pathParameters']:
        return error_response(400, "Product ID is required")

    try:
        # Extract the product ID from the path parameters
        product_id = event["pathParameters"]["id"]
        print(f"Searching for product with ID: {product_id}")

        # Find the product with the specified ID
        product = get_product_by_id(product_id)

        if not product:
            # return 404 if product was not found
            print(f"Product with ID {product_id} not found")
            return error_response(404, "Product not found")

        print(f"Successfully retrieved product: {json.dumps(product)}")

        return {
            "statusCode": 200,
            "headers": HEADERS,
            "body": json.dumps(product),
        }

    except Exception as e:
        print(f"Error: An unexpected error occurred: {str(e)}")
        return error_response(500, "Internal Server Error")


def get_product_by_id(product_id: str):
    """
    Retrieves a specific product and its stock information by product ID.
    """

    dynamodb = boto3.resource("dynamodb", region_name=os.getenv("AWS_REGION"))
    stock_table_name = os.getenv("STOCK_TABLE_NAME")
    product_table_name = os.getenv("PRODUCTS_TABLE_NAME")

    product_table = dynamodb.Table(product_table_name)
    stock_table = dynamodb.Table(stock_table_name)

    # Get product
    product_response = product_table.get_item(Key={"id": product_id})
    product = product_response.get("Item")

    if not product:
        return None

    # Get stock information
    stock_response = stock_table.get_item(Key={"product_id": product_id})

    # Add stock information to the product
    product["count"] = int(stock_response.get(
        "Item", {"count": 0}).get("count"))
    product['price'] = float(product['price'])

    return product


def error_response(status_code: int, message: str):
    """
    Helper function to create error responses.
    """

    return {
        "statusCode": status_code,
        "headers": HEADERS,
        "body": json.dumps({"message": message}),
    }
