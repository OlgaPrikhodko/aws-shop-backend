import json
import os
import boto3


s3 = boto3.client('s3')


def handler(event, _context):
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

    file_name = "products.csv"  # query_parameters['name']
    bucket_name = "task-5-import-csv-for-shop"  # os.environ['BUCKET_NAME']
    key = f"uploaded/{file_name}"

    print(f"bucket name - {bucket_name}")
    print(f"import file - {key}")

    params = {
        'Bucket': bucket_name,
        'Key': key
    }

    try:
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
                'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
                'Access-Control-Allow-Credentials': True
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
