import json
import os
import boto3


s3 = boto3.client('s3')


def handler(event, _context):
    """
    Lambda function handler that generates a presigned URL for S3 file upload.
    """
    # Get the filename from query parameters
    query_parameters = event.get('queryStringParameters', {})
    if not query_parameters or 'name' not in query_parameters:
        return {
            'statusCode': 400,
            'headers': {
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': 'File name is required'})
        }

    file_name = query_parameters['name']
    bucket_name = os.environ['BUCKET_NAME']
    key = f"uploaded/{file_name}"

    print(f"bucket name - {bucket_name}")
    print(f"import file - {key}")

    params = {
        'Bucket': bucket_name,
        'Key': key,
        "ContentType": "text/csv"
    }

    try:
        # Generate presigned URL for PUT operation
        # URL will be valid for 1 hour (3600 seconds)
        signed_url = s3.generate_presigned_url(
            'put_object',
            Params=params,
            ExpiresIn=3600
        )
        print(f"signed url - {signed_url}")

        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET,OPTIONS',
                'Access-Control-Allow-Headers': 'Authorization,Content-Type',
            },
            'body': signed_url
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': str(e)})
        }
