import io
import csv
import os
import boto3


s3 = boto3.client('s3')


def handler(event, _context):
    """
    Lambda function handler that triggered by s3 event, fired by changes in the uploaded folder .
    """
    bucket_name = os.environ['BUCKET_NAME']

    try:
        for record in event.get('Records', []):
            # Extract the object key (file name) from the event
            key = record['s3']['object']['key']
            file_name = key.split('/')[-1]

            print(f"Processing file {key}")

            # Get the object from s3
            response = s3.get_object(Bucket=bucket_name, Key=key)

            # Read file content
            body = response['Body']
            csv_file = io.StringIO(body.read().decode('utf-8'))

            # Parse csv
            reader = csv.DictReader(csv_file)

            print("File rows: ")
            for row in reader:
                print(row)

            copy_source = {'Bucket': bucket_name, 'Key': key}
            parsed_key = key.replace('uploaded/', 'parsed/')

            # Copy the object to the parsed folder
            s3.copy_object(Bucket=bucket_name,
                           CopySource=copy_source, Key=parsed_key)

            # Delete the original object from the uploaded folder
            if key != 'uploaded/':
                s3.delete_object(Bucket=bucket_name, Key=key)

            print(f"File from '{file_name}' moved to parsed folder.")
    except:
        print("Error processing file")
        raise
