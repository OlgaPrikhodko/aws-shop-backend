import json
import os
import boto3


def handler(_event, _context):
    """
    Lambda handler for GET /products endpoint.
    Returns a list of all products with their stock information.
    """
    # Log incoming request
    print("GET /products request received")

    try:
        products = get_products_with_stocks()
        print(f"Successfully retrieved {len(products)} products")

        return {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET",
                "Access-Control-Allow-Credentials": True,
                "Content-Type": "application/json",
            },
            "body": json.dumps(products),
        }
    except Exception as e:
        print(f"Error occurred: {str(e)}")

        return {
            "statusCode": 500,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET",
                "Access-Control-Allow-Credentials": True,
                "Content-Type": "application/json",
            },
            "body": json.dumps({"error": str(e)}),
        }


def get_products_with_stocks():
    dynamodb = boto3.resource("dynamodb", region_name=os.getenv("AWS_REGION"))

    product_table_name = os.getenv("PRODUCTS_TABLE_NAME")
    stock_table_name = os.getenv("STOCK_TABLE_NAME")

    product_table = dynamodb.Table(product_table_name)
    stock_table = dynamodb.Table(stock_table_name)

    # get all products
    product_response = product_table.scan()
    product_items = product_response.get("Items", [])

    # get stock information
    stock_response = stock_table.scan()
    stock_items = {item['product_id']: item['count']
                   for item in stock_response['Items']}

    # combine product information with stock information
    products = []
    for product in product_items:
        product_id = product['id']
        product['count'] = int(stock_items.get(product_id, 0))
        product['price'] = float(product['price'])
        products.append(product)

    return products
