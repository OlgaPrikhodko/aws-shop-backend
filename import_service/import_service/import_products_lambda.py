from aws_cdk import Stack, aws_s3 as s3, aws_lambda as lambda_

from constructs import Construct


class ImportProductsLambda(Stack):
    """
    CDK Stack that creates a Lambda function with S3 bucket permissions.

    This stack:
    1. References an existing S3 bucket
    2. Creates a Lambda function
    3. Grants the Lambda function permissions to interact with the bucket
    """

    def __init__(self, scope: Construct, construct_id: str, bucket_name: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Reference an existing S3 bucket using its name
        bucket = s3.Bucket.from_bucket_name(self, 'ImportProductsLambda',
                                            bucket_name=bucket_name)

        # Create Lambda function
        self.import_products_file = lambda_.Function(
            self,
            'ImportProductsFile',
            runtime=lambda_.Runtime.PYTHON_3_12,
            handler='import_products_file.handler',
            code=lambda_.Code.from_asset('import_service/lambda_func/'),
            environment={'BUCKET_NAME': bucket.bucket_name}
        )

        # Grant permissions to the Lambda function:
        bucket.grant_put(self.import_products_file)
        bucket.grant_read_write(self.import_products_file)
