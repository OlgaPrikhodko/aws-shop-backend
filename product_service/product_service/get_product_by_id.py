from aws_cdk import (
    Stack,
    aws_lambda as lambda_
)
from constructs import Construct


class GetProductById(Stack):
    """
    CDK Stack that creates a Lambda function for retrieving products by ID.

    Attributes:
        get_product_by_id (_lambda.Function): An AWS Lambda function that
            handles product by id retrieval.
    """

    def __init__(self, scope: Construct, construct_id: str, environment: dict) -> None:
        """
        Initialize GetProductById stack.

        Args:
            scope: CDK app construct scope
            construct_id: Unique identifier for the stack
            environment: Environment variables for the Lambda function

        """
        super().__init__(scope, construct_id)

        # Define an AWS Lambda resource
        self.get_product_by_id = lambda_.Function(
            self,
            "GetProductByIdHandler",
            runtime=lambda_.Runtime.PYTHON_3_12,
            handler="product_by_id.handler",
            code=lambda_.Code.from_asset("product_service/lambda_func/"),
            environment=environment
        )
