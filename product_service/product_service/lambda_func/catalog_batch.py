import json
import os
import boto3


dynamodb_client = boto3.client('dynamodb')
dynamodb = boto3.resource("dynamodb", region_name=os.getenv("AWS_REGION"))
sns_client = boto3.client('sns')


def handler(event, _context):
    stock_table_name = os.environ['STOCK_TABLE_NAME']
    product_table_name = os.environ['PRODUCTS_TABLE_NAME']
    sns_topic_arn = os.environ['SNS_TOPIC_ARN']

    products_for_sns = []

    # Check if there are any records
    if not event.get('Records'):
        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'No records to process'}),
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Credentials': True,
                'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
            }
        }

    for record in event['Records']:
        try:
            record_data = json.loads(record['body'])

            # Simple validation that are all fields in place
            required_fields = ['id', 'title', 'description', 'price', 'count']
            for field in required_fields:
                if field not in record_data:
                    return {
                        'statusCode': 400,
                        'body': json.dumps({'message': f'Invalid input: {field} is missing'})
                    }

            product_item = {
                'id': {'S': str(record_data['id'])},
                'title': {'S': record_data['title']},
                'description': {'S': record_data['description']},
                'price': {'N': str(record_data['price'])}
            }

            stock_item = {
                'product_id': {'S': str(record_data['id'])},
                'count': {'N': str(record_data['count'])}
            }

            # save to DynamoDB
            dynamodb_client.transact_write_items(
                TransactItems=[
                    {
                        'Put': {
                            'TableName': product_table_name,
                            'Item': product_item
                        }
                    },
                    {
                        'Put': {
                            'TableName': stock_table_name,
                            'Item': stock_item
                        }
                    }
                ]
            )

            products_for_sns.append({
                'id': str(record_data['id']),
                'title': record_data['title'],
                'description': record_data['description'],
                'price': record_data['price'],
                'count': record_data['count']
            })

        except Exception as e:
            print(f"Error processing record: {str(e)}")
            continue

    # Send SNS notification after processing all records
    if products_for_sns:
        sns_message = {
            'default': json.dumps({
                'message': 'New product added',
                'products': products_for_sns
            })
        }

        response = sns_client.publish(
            TopicArn=sns_topic_arn,
            Message=json.dumps(sns_message),
            MessageStructure='json'
        )

        print(f"Message sent to SNS topic: {response['MessageId']}")

    return {
        'statusCode': 200,
        'body': json.dumps({'message': 'Products added successfully'}),
        'headers': {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Credentials': True,
            'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
        }
    }
