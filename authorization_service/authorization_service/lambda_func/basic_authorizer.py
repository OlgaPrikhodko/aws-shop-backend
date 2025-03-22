import os
import base64


def handler(event, _context):
    print(event)

    # Check if Authorization header exists
    auth_header = event['authorizationToken']

    if not auth_header:
        return {
            'statusCode': 401,
            'body': 'Unauthorized'
        }

    # Remove 'Basic ' prefix from the Authorization header
    encoded_credentials = auth_header.split(' ')[1]

    # Decode the Base64-encoded credentials
    decoded_credentials = base64.b64decode(encoded_credentials).decode('utf-8')
    username, password = decoded_credentials.split('=')

    # Get stored credentials from environment variables
    stored_password = os.environ[username]

    if not stored_password or stored_password != password:
        return {
            'statusCode': 403,
            'body': 'Forbidden'
        }

    return generate_policy(username, 'Allow', event['methodArn'])


def generate_policy(principal_id, effect, resource):
    auth_response = {
        'principalId': principal_id
    }
    if effect and resource:
        policy_document = {
            'Version': '2012-10-17',
            'Statement': [{
                'Action': 'execute-api:Invoke',
                'Effect': effect,
                'Resource': resource
            }]
        }
        auth_response['policyDocument'] = policy_document

    return auth_response
