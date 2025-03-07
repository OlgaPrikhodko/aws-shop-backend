from aws_cdk import (
    Stack,
    aws_dynamodb as dynamodb,
)
from constructs import Construct

from product_service.api_gateway import ApiGateway
from product_service.get_products import GetProducts
from product_service.get_product_by_id import GetProductById
from product_service.create_product import CreateProduct


class ProductServiceStack(Stack):
    """
    ProductServiceStack - A serverless stack for managing product-related operations in AWS

    This stack creates a serverless architecture for managing products and their stock information
    using AWS services including DynamoDB, Lambda, and API Gateway.

    Components:
    -----------
    DynamoDB Tables:
        - products: Stores product information including id, title, description, and price
        - stock: Stores stock information for products including id and count

    Lambda Functions:
        - GetProducts: Retrieves list of all products with their stock information
        - GetProductById: Retrieves a specific product by ID with its stock information
        - CreateProduct: Creates a new product with its initial stock information

    API Gateway endpoints:
        - GET /products: Returns all products with their stock information
        - GET /products/{id}: Returns specific product by ID
        - POST /products: Creates a new product

    Environment Variables:
        - PRODUCTS_TABLE_NAME: Name of the products DynamoDB table
        - STOCK_TABLE_NAME: Name of the stock DynamoDB table

    Permissions:
        - GetProducts Lambda: Read/Write access to both products and stock tables
        - GetProductById Lambda: Read/Write access to both products and stock tables
        - CreateProduct Lambda: Read/Write access to both products and stock tables

    Example Usage:
    -------------
    Deployment:
        cdk deploy ProductServiceStack

    API Endpoints Usage:
        GET /products
            Returns: List of all products with their stock information

        GET /products/{id}
            Parameters: id (string) - The unique identifier of the product
            Returns: Single product with its stock information

        POST /products
            Body: {
                "title": "string",
                "description": "string",
                "price": number,
                "count": number
            }
            Returns: Created product information

    Response Format:
        {
            "id": "string",        # Unique identifier of the product
            "title": "string",     # Name/title of the product
            "description": "string", # Detailed description of the product
            "price": number,       # Price of the product
            "count": number        # Current stock count
        }

    Error Handling:
        - Returns 404 if product is not found
        - Returns 400 for invalid input
        - Returns 500 for server errors

    Dependencies:
        - aws_cdk.aws_dynamodb
        - aws_cdk.aws_lambda
        - aws_cdk.aws_apigateway
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

        # Create Lambda function for creating a new product
        # This function will handle the POST '/products' endpoint
        create_product_fn = CreateProduct(
            self, 'CreateProduct', environment=environment)

        # Give read permissions to both Lambda functions for the products table
        products_table.grant_read_data(get_products_fn.get_product_list)
        products_table.grant_read_data(
            get_product_by_id_fn.get_product_by_id)

        # Give read permissions to both Lambda functions for the stock table
        stock_table.grant_read_data(get_products_fn.get_product_list)
        stock_table.grant_read_data(
            get_product_by_id_fn.get_product_by_id)

        # Give write permissions to the create_product_fn for both tables
        products_table.grant_write_data(create_product_fn.create_product)
        stock_table.grant_write_data(create_product_fn.create_product)

        ApiGateway(self, "APIGateway",
                   get_products_fn=get_products_fn.get_product_list,
                   get_product_by_id_fn=get_product_by_id_fn.get_product_by_id,
                   create_product_fn=create_product_fn.create_product)
