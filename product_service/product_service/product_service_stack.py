from aws_cdk import (
    Stack,
)
from constructs import Construct

from product_service.get_products import GetProducts
from product_service.api_gateway import ApiGateway


class ProductServiceStack(Stack):
    """
    Main CDK Stack for the Product Service application.

    This stack is responsible for creating and configuring all AWS resources
    needed for the product service, including Lambda functions and API Gateway.
    It serves as the primary infrastructure definition for the product catalog system.

    Attributes:
        None

    Example:
        app = cdk.App()
        ProductServiceStack(app, "ProductServiceStack")
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

        # Create Lambda function for getting products
        # This function will handle the GET '/products' endpoint
        get_products_fn = GetProducts(self, 'ProductList')

        ApiGateway(self, "APIGateway",
                   get_products_fn=get_products_fn.get_product_list)
