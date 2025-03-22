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

        basic_authorizer_lambda = lambda_.Function.from_function_name(
            self, "authFunction", "AuthFunction")

        # Create REST API
        api = apigateway.RestApi(
            self, 'ImportProductsApi',
            rest_api_name='Import Products Api',
            description='API Gateway for import service'
        )

        # Create Lambda authorizer
        authorizer = apigateway.TokenAuthorizer(
            self, 'BasicAuthorizer', handler=basic_authorizer_lambda,
            identity_source='method.request.header.Authorization'
        )

        # Create '/import' resource endpoint in API Gateway
        # This path will be used for importing products via signed S3 URLs
        resource = api.root.add_resource('import')

        # Configure GET /import endpoint with Lambda integration and Basic Auth
        resource.add_method(
            'GET',
            apigateway.LambdaIntegration(import_products_fn),
            authorization_type=apigateway.AuthorizationType.CUSTOM,
            authorizer=authorizer  # Auth Lambda authorizer
        )

        resource.add_method(
            "OPTIONS",
            apigateway.MockIntegration(
                integration_responses=[
                    apigateway.IntegrationResponse(
                        status_code="200",
                        response_parameters={
                            "method.response.header.Access-Control-Allow-Headers": "'Authorization,Content-Type'",
                            "method.response.header.Access-Control-Allow-Origin": "'*'",
                            "method.response.header.Access-Control-Allow-Methods": "'GET,OPTIONS'",
                        },
                    )
                ],
                passthrough_behavior=apigateway.PassthroughBehavior.NEVER,
                request_templates={"application/json": '{"statusCode": 200}'},
            ),
            method_responses=[
                apigateway.MethodResponse(
                    status_code="200",
                    response_parameters={
                        "method.response.header.Access-Control-Allow-Headers": True,
                        "method.response.header.Access-Control-Allow-Origin": True,
                        "method.response.header.Access-Control-Allow-Methods": True,
                    },
                )
            ],
        )
