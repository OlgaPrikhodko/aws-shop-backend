from aws_cdk import (
    Stack,
    aws_lambda as lambda_,
    aws_apigateway as apigateway,

)

from constructs import Construct


class ApiGateway(Stack):
    """
    CDK Stack that creates an API Gateway with Lambda integration.

    This stack:
    1. Creates a REST API
    2. Adds an 'import' resource
    3. Configures a GET method with Lambda integration
    """

    def __init__(self, scope: Construct, construct_id: str,
                 import_products_fn: lambda_.Function, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create REST API
        api = apigateway.RestApi(
            self, 'ImportProductsApi',
            rest_api_name='Import Products Api',
            description='API Gateway for import service'
        )

        # Create 'import' resource
        # This adds a new resource path '/import' to the API
        resource = api.root.add_resource('import')

        # Add GET method to the resource
        # This creates an endpoint: GET /import
        resource.add_method(
            'GET',
            apigateway.LambdaIntegration(
                import_products_fn)
        )
