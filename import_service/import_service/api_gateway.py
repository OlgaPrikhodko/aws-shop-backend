from aws_cdk import (
    Stack,
    aws_lambda as lambda_,
    aws_apigateway as apigateway,

)

from constructs import Construct


class ApiGateway(Stack):
    def __init__(self, scope: Construct, construct_id: str,
                 import_products_fn: lambda_.Function, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        api = apigateway.RestApi(
            self, 'ImportProductsApi',
            rest_api_name='Import Products Api',
            description='API Gateway for import service'
        )

        # create resource and method
        resource = api.root.add_resource('import')

        resource.add_method(
            'GET',
            apigateway.LambdaIntegration(
                import_products_fn)
        )
