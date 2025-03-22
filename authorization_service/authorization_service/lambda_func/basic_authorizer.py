import os
import base64


def handler(event, _context):
    print("Auth Lambda invoked with event:", event)

    try:
        auth_header = event.get('authorizationToken', '')

        if not auth_header.startswith("Basic "):
            raise ValueError("Invalid Authorization header format")

        parts = auth_header.split(" ")
        if len(parts) != 2:
            raise ValueError("Malformed Authorization header")

        encoded_credentials = parts[1]

        # Decode base64
        try:
            decoded_credentials = base64.b64decode(
                encoded_credentials).decode("utf-8")
        except Exception as e:
            raise ValueError(f"Base64 decoding failed: {str(e)}")

        # Split credentials
        if '=' in decoded_credentials:
            username, password = decoded_credentials.split('=', 1)
        elif ':' in decoded_credentials:
            username, password = decoded_credentials.split(':', 1)
        else:
            raise ValueError(
                "Credentials must be in 'username=password' or 'username:password' format")

        # Check environment
        stored_password = os.environ.get(username)

        if not stored_password or stored_password != password:
            return {
                'statusCode': 403,
                'body': 'Forbidden'
            }

        print(f"Auth success for user: {username}")
        return generate_policy(username, 'Allow', event['methodArn'])

    except Exception as e:
        print("Unhandled error in authorizer:", str(e))
        return generate_policy("anonymous", 'Deny', event.get('methodArn', '*'))


def generate_policy(principal_id, effect, resource):
    return {
        'principalId': principal_id,
        'policyDocument': {
            'Version': '2012-10-17',
            'Statement': [{
                'Action': 'execute-api:Invoke',
                'Effect': effect,
                'Resource': resource
            }]
        }
    }
