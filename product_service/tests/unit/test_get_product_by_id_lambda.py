from unittest.mock import Mock, patch
import json

from product_service.lambda_func.product_by_id import handler


# Sample test data
MOCK_PRODUCTS = [
    {"id": "1", "title": "Citrus", "price": 5.99},
    {"id": "2", "title": "Palm", "price": 10.99}
]


def test_product_by_id_success():
    # Arrange
    event = {
        'pathParameters': {
            'id': '1'
        }
    }
    context = Mock()
    expected_product = MOCK_PRODUCTS[0]

    # Act
    response = handler(event, context)

    # Assert
    # Assert
    assert response['statusCode'] == 200
    assert response['headers'] == {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET",
        "Access-Control-Allow-Credentials": True,
        "Content-Type": "application/json",
    }

    product = json.loads(response['body'])
    expected_product = {
        "id": "1",
        "title": "Citrus Calamondin Grafted Trellis",
        "price": 29.90
    }
    assert product == expected_product


def test_product_by_id_not_found():
    # Arrange
    event = {
        'pathParameters': {
            'id': '999'  # Non-existent ID
        }
    }
    context = {}

    # Act
    response = handler(event, context)

    # Assert
    assert response['statusCode'] == 404
    assert response['headers'] == {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET",
        "Access-Control-Allow-Credentials": True,
        "Content-Type": "application/json",
    }

    body = json.loads(response['body'])
    assert body == {"message": "Product not found"}
