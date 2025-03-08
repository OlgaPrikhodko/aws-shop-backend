from aws_cdk import (
    Stack,
)
from constructs import Construct

from import_service.import_products_lambda import ImportProductsLambda
from import_service.api_gateway import ApiGateway


class ImportServiceStack(Stack):
    """
    Main CDK Stack that sets the complete import service infrastructure.
    """

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        bucket_name = 'task-5-import-csv-for-shop'

        # Create the ImportProductsLambda stack
        # This creates the Lambda function with necessary S3 permissions
        import_products_lambda = ImportProductsLambda(
            self,
            'ImportProductsLambda',
            bucket_name=bucket_name
        )

        # Create API Gateway to expose the Lambda function
        # This will create a REST API that can trigger the Lambda function
        ApiGateway(
            self,
            'ApiGateway',
            import_products_fn=import_products_lambda.import_products_file
        )
