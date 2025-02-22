from unittest.mock import Mock
import json

from product_service.lambda_func import product_list

# Sample test data
MOCK_PRODUCTS = [
    {"id": "1", "title": "Citrus", "price": 5.99},
    {"id": "2", "title": "Palm", "price": 10.99}
]


def test_product_list_success():
    # Arrange
    event = {}
    context = Mock()

    # Act
    response = product_list.handler(event, context)

    # Assert
    assert response['statusCode'] == 200
    assert response['headers'] == {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET",
        "Access-Control-Allow-Credentials": True,
        "Content-Type": "application/json",
    }

    # Test data structure without caring about specific values
    products = json.loads(response['body'])

    assert isinstance(products, list)
    for product in products:
        assert isinstance(product, dict)
        assert all(key in product for key in ['id', 'title', 'price'])
        assert isinstance(product['id'], str)
        assert isinstance(product['title'], str)
        assert isinstance(product['price'], (int, float))


#     # Arrange
#     event = {
#         'pathParameters': {
#             'productId': 'non-existent-id'
#         }
#     }
#     context = Mock()

#     # Act
#     response = product_by_id.handler(event, context)

#     # Assert
#     assert response['statusCode'] == 404
#     assert response['headers'] == {
#         "Access-Control-Allow-Origin": "*",
#         "Access-Control-Allow-Methods": "GET",
#         "Access-Control-Allow-Credentials": True,
#         "Content-Type": "application/json",
#     }

#     error_response = json.loads(response['body'])
#     assert 'message' in error_response
#     assert error_response['message'] == 'Product not found'
