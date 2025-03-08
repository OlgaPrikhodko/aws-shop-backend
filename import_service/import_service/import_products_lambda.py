from aws_cdk import Stack, aws_s3 as s3, aws_lambda as lambda_

from constructs import Construct


class ImportProductsLambda(Stack):
    def __init__(self, scope: Construct, construct_id: str, bucket_name: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        bucket = s3.Bucket.from_bucket_name(self, 'ImportProductsLambda',
                                            bucket_name=bucket_name)

        self.import_products_file = lambda_.Function(
            self,
            'ImportProductsFile',
            runtime=lambda_.Runtime.PYTHON_3_12,
            handler='import_products_file.handler',
            code=lambda_.Code.from_asset('import_service/lambda_func/'),
            environment={'BUCKET_NAME': bucket.bucket_name}
        )

        bucket.grant_put(self.import_products_file)
        bucket.grant_read_write(self.import_products_file)
