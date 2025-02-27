from aws_cdk import (
    Stack,
    aws_lambda as _lambda,
)

from constructs import Construct


class GetProducts(Stack):
    """
    Construct for the GetProducts Lambda function.


    """

    def __init__(self, scope: Construct, construct_id: str, environment: dict) -> None:
        """
        Initializes the GetProducts stack and defines the AWS Lambda function.

        Args:
            scope (Construct): The parent construct (usually an AWS CDK app or another stack).
            construct_id (str): A unique identifier for this stack.
            environment: Environment variables for the Lambda function
        """
        super().__init__(scope, construct_id)

        # Defines an AWS Lambda resource
        self.get_product_list = _lambda.Function(
            self,
            "GetProductListHandler",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="product_list.handler",
            code=_lambda.Code.from_asset("product_service/lambda_func/"),
            environment=environment
        )
