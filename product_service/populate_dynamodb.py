import boto3
import uuid
from typing import Dict, Any

# Initialize DynamoDB client
dynamodb = boto3.resource('dynamodb')

# Reference to our tables
products_table = dynamodb.Table('products')
stocks_table = dynamodb.Table('stocks')


# Test data

test_products = [
    {
        "id": str(uuid.uuid4()),
        "title": "Citrus Calamondin",
        "description": "Miniature citrus tree that produces fragrant flowers and fruits",
        "price": 49
    },
    {
        "id": str(uuid.uuid4()),
        "title": "Fiddle Leaf Fig",
        "description": "Large-leaved indoor plant that thrives in bright, indirect light",
        "price": 49
    },
    {
        "id": str(uuid.uuid4()),
        "title": "Snake Plant",
        "description": "Hardy and air-purifying plant with striking upright leaves",
        "price": 35
    },
    {
        "id": str(uuid.uuid4()),
        "title": "Aloe Vera",
        "description": "Succulent plant known for its soothing gel and low maintenance",
        "price": 25
    },
    {
        "id": str(uuid.uuid4()),
        "title": "Peace Lily",
        "description": "Elegant flowering plant that helps purify indoor air",
        "price": 30
    },
    {
        "id": str(uuid.uuid4()),
        "title": "Pothos",
        "description": "Fast-growing vine plant that thrives in various lighting conditions",
        "price": 20
    },
    {
        "id": str(uuid.uuid4()),
        "title": "Monstera Deliciosa",
        "description": "Tropical plant with unique split leaves, perfect for home decor",
        "price": 60
    },
    {
        "id": str(uuid.uuid4()),
        "title": "Spider Plant",
        "description": "Resilient and air-purifying plant with arching green leaves",
        "price": 22
    },
    {
        "id": str(uuid.uuid4()),
        "title": "Citrus Tree",
        "description": "Miniature citrus tree that produces fragrant flowers and fruits",
        "price": 80
    },
    {
        "id": str(uuid.uuid4()),
        "title": "Parlor Palm",
        "description": "Low-maintenance palm that thrives in low-light conditions",
        "price": 40
    },
    {
        "id": str(uuid.uuid4()),
        "title": "Jade Plant",
        "description": "A popular succulent symbolizing prosperity and good luck",
        "price": 28
    }
]


def put_product(product: Dict[str, Any]) -> None:
    """Insert a product into the products table"""
    try:
        products_table.put_item(Item=product)
        print(f"Added product: {product['title']}")
    except Exception as e:
        print(f"Error adding product {product['title']}: {str(e)}")


def put_stock(product_id: str, count: int) -> None:
    """Insert a stock record into the stocks table"""
    try:
        stocks_table.put_item(
            Item={
                "product_id": product_id,
                "count": count
            }
        )
        print(f"Added stock for product: {product_id}")
    except Exception as e:
        print(f"Error adding stock for product {product_id}: {str(e)}")


def main():
    # Add products and their corresponding stock
    for product in test_products:
        # Add product
        put_product(product)

        # Add random stock count (between 1-100) for each product
        import random
        put_stock(product["id"], random.randint(1, 100))


if __name__ == "__main__":
    main()
