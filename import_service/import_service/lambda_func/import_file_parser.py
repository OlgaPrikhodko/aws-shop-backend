import io
import csv
import os
import json
import boto3


s3 = boto3.client('s3')
sqs = boto3.client('sqs', region_name=os.getenv("AWS_REGION"))


def handler(event, _context):
    """
    Lambda function handler that triggered by s3 event, fired by changes in the uploaded folder .
    """
    bucket_name = os.environ['BUCKET_NAME']

    queue_url = os.environ['QUEUE_URL']

    try:
        for record in event.get('Records', []):
            # Extract the object key (file name) from the event
            key = record['s3']['object']['key']

            # Get the object from s3
            response = s3.get_object(Bucket=bucket_name, Key=key)

            # Read file content
            body = response['Body']
            csv_file = io.StringIO(body.read().decode('utf-8'))

            # Parse csv
            reader = csv.DictReader(csv_file)

            for row in reader:
                print(json.dumps(row))
                sqs.send_message(QueueUrl=queue_url,
                                 MessageBody=json.dumps(row))

            # Copy the object to the parsed folder
            copy_source = {'Bucket': bucket_name, 'Key': key}
            parsed_key = key.replace('uploaded/', 'parsed/')

            s3.copy_object(Bucket=bucket_name,
                           CopySource=copy_source, Key=parsed_key)

            # Delete the original object from the uploaded folder
            if key != 'uploaded/':
                s3.delete_object(Bucket=bucket_name, Key=key)
    except:
        print("Error processing file")
        raise
