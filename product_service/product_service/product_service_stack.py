from aws_cdk import (
    Stack,
    aws_dynamodb as dynamodb,
)
from constructs import Construct

from product_service.api_gateway import ApiGateway
from product_service.get_products import GetProducts
from product_service.get_product_by_id import GetProductById


class ProductServiceStack(Stack):
    """
    ProductServiceStack - A serverless stack for managing product-related operations


    Components:
    - DynamoDB Tables:
    - products: Stores product information
    - stock: Stores stock information for products

    - Lambda Functions:
    - GetProducts: Retrieves list of all products
    - GetProductById: Retrieves a specific product by ID

    - API Gateway endpoints:
    - GET / products: Returns all products
    - GET / products/{id}: Returns specific product by ID

    Environment Variables:
    - PRODUCTS_TABLE_NAME: Name of the products DynamoDB table
    - STOCK_TABLE_NAME: Name of the stock DynamoDB table

    Permissions:
    - Lambda functions have read access to both products and stock tables


    Example Usage:

    # To deploy the stack:
    cdk deploy ProductServiceStack

    # API Endpoints:
    GET /products - Returns all products with their stock information
    GET /products/{id} - Returns a specific product with its stock information

    Response Format:
    {
        "id": "string",
        "title": "string",
        "description": "string",
        "price": number,
        "count": number
    }
    """

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        """
        Initialize the Product Service Stack.

        Args:
            scope (Construct): The scope in which to define this construct.
                Usually an instance of cdk.App or another Stack.
            construct_id (str): The ID of the construct. Used to generate
                unique identifiers for AWS resources.
            **kwargs: Additional keyword arguments passed to the parent Stack class.
        """
        super().__init__(scope, construct_id, **kwargs)

        # Define the names of DynamoDB tables that will be used in the application
        products_table_name = 'products'
        stock_table_name = 'stocks'

        # Create references to existing DynamoDB tables using their names
        # from_table_name method is used when the tables already exist and we want to reference them
        products_table = dynamodb.Table.from_table_name(
            self, "ProductsTable", products_table_name)
        stock_table = dynamodb.Table.from_table_name(
            self, "StockTable", stock_table_name)

        # Create an environment variables dictionary that will be passed to Lambda functions
        # This allows Lambda functions to know which tables to interact with
        environment = {
            "PRODUCTS_TABLE_NAME": products_table_name,
            "STOCK_TABLE_NAME": stock_table_name,
        }

        # Create Lambda function for getting a list of all products
        # This function will handle the GET '/products' endpoint
        get_products_fn = GetProducts(
            self, 'ProductList', environment=environment)

        # Create Lambda function for getting a single product based on ID
        # This function will handle the GET '/products/{id}' endpoint
        get_product_by_id_fn = GetProductById(
            self, 'ProductById', environment=environment)

        # Grant read permissions to Lambda functions
        # Give read permissions to both Lambda functions for the products table
        products_table.grant_read_data(get_products_fn.get_product_list)
        products_table.grant_read_data(get_product_by_id_fn.get_product_by_id)

        # Give read permissions to both Lambda functions for the stock table
        stock_table.grant_read_data(get_products_fn.get_product_list)
        stock_table.grant_read_data(get_product_by_id_fn.get_product_by_id)

        ApiGateway(self, "APIGateway",
                   get_products_fn=get_products_fn.get_product_list,
                   get_product_by_id_fn=get_product_by_id_fn.get_product_by_id)
