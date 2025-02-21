from aws_cdk import (
    Stack,
    aws_lambda as lambda_,
    aws_apigateway as apigateway
)

from constructs import Construct


class ApiGateway(Stack):
    """
    A CDK Stack that creates an API Gateway for the Product Service.

    This stack sets up a REST API with endpoints to handle product-related operations.
    It creates an API Gateway instance and configures routes for product management.
    """

    def __init__(
            self,
            scope: Construct, constructor_id: str,
            get_products_fn: lambda_.Function,
            **kwargs
    ) -> None:
        """
        Initialize the API Gateway Stack.

        Args:
            scope (Construct): The scope in which to define this construct.
            constructor_id (str): The ID of the construct.
            get_products_fn (_lambda): Lambda function for getting products list.
            **kwargs: Additional keyword arguments to pass to the parent Stack.
        """

        super().__init__(scope, constructor_id, **kwargs)

        # Create REST API instance
        api = apigateway.RestApi(
            self, "ProductServiceApi", rest_api_name="ProductsApi"
        )

        # Add '/products' resource to the API
        products_resource = api.root.add_resource("products")

        # Configure GET method for '/products' endpoint with Lambda integration
        products_resource.add_method(
            "GET", apigateway.LambdaIntegration(
                get_products_fn)
        )
