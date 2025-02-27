from aws_cdk import (
    Stack,
    aws_lambda as _lambda,
)

from constructs import Construct


class GetProducts(Stack):
    """
    AWS CDK Stack for deploying the GetProducts Lambda function.

    This class defines an AWS Cloud Development Kit (CDK) stack that deploys
    a Lambda function for retrieving a list of products.

    Attributes:
        get_product_list (_lambda.Function): An AWS Lambda function that
            handles product list retrieval.

    Args:
        scope (Construct): The parent construct (usually an AWS CDK app or another stack).
        construct_id (str): A unique identifier for this stack.
        **kwargs: Additional keyword arguments for the base Stack class.
    """

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        """
        Initializes the GetProducts stack and defines the AWS Lambda function.

        The Lambda function is deployed from the specified source directory
        and is configured to use Python 3.12 as its runtime.

        """
        super().__init__(scope, construct_id, **kwargs)

        # Defines an AWS Lambda resource
        self.get_product_list = _lambda.Function(
            self,
            "GetProductListHandler",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="product_list.handler",
            code=_lambda.Code.from_asset("product_service/lambda_func/"),
        )
