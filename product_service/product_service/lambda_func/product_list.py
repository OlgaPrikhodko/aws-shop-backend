import json


def handler(_event, _context):
    products = [
        {"id": "1", "title": "Citrus Calamondin Grafted Trellis", "price": 29.90},
        {"id": "2", "title": "European Fan Palm - Chamaerops humilis", "price": 19.99},
        {"id": "3", "title": "Dipsis - Dipsis lutescens", "price": 3.49},
    ]

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
