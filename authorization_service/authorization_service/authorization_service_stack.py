import os
import dotenv

from aws_cdk import (
    Stack,
    aws_lambda as lambda_,
)
from constructs import Construct


class AuthorizationServiceStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        dotenv.load_dotenv()

        login = 'OlgaPrikhodko'
        SECRET_KEY = os.getenv(login)

        lambda_.Function(
            self, 'BasicAuthorizationLambda',
            runtime=lambda_.Runtime.PYTHON_3_12,
            handler='basic_authorizer.handler',
            code=lambda_.Code.from_asset('authorization_service/lambda_func/'),
            environment={
                'login': SECRET_KEY
            },
            function_name='AuthFunction'
        )
