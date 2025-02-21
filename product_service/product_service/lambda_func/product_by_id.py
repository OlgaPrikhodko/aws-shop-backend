import json


def handler(event, _context):
    products = [
        {"id": 1, "title": "Citrus Calamondin Grafted Trellis", "price": 29.90},
        {"id": 2, "title": "European Fan Palm - Chamaerops humilis", "price": 19.99},
        {"id": 3, "title": "Dipsis - Dipsis lutescens", "price": 3.49},
    ]

    # Extract the product ID from the path parameters
    product_id = event["pathParameters"]["id"]

    # Find the product with the specified ID
    product = next((p for p in products if p["id"] == product_id), None)

    if product:
        return {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET",
                "Access-Control-Allow-Credentials": True,
                "Content-Type": "application/json",
            },
            "body": json.dumps(product),
        }

    # return 404 if product was not found
    return {
        "statusCode": 404,
        "headers": {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET",
            "Access-Control-Allow-Credentials": True,
            "Content-Type": "application/json",
        },
        "body": json.dumps({"message": "Product not found"}),
    }
