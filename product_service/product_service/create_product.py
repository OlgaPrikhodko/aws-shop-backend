from aws_cdk import (
    Stack,
    aws_lambda as lambda_
)

from constructs import Construct


class CreateProduct(Stack):
    """
    Constructs the stack for the lambda function to put products into the target DynamoDB table.
    """

    def __init__(self, scope: Construct, construct_id: str, environment: dict) -> None:
        super().__init__(scope, construct_id)

        # Lambda function to put products into the target DynamoDB table.
        self.create_product = lambda_.Function(
            self,
            "CreateProductHandler",
            runtime=lambda_.Runtime.PYTHON_3_12,
            handler="create_product.handler",
            code=lambda_.Code.from_asset("product_service/lambda_func/"),
            environment=environment
        )
