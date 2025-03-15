from aws_cdk import (
    Stack,
    aws_lambda as lambda_,
    aws_s3 as s3,
    aws_s3_notifications as s3_notifications,
    aws_sqs as sqs
)
from constructs import Construct


class FileParserLambda(Stack):
    """
    AWS CDK Stack that creates a Lambda function for parsing files in an S3 bucket.

    This stack sets up a Lambda function that processes files from a specified S3 bucket.
    It configures necessary IAM permissions for the Lambda to read, write, and delete objects
    from the bucket.
import boto3

    Attributes:
        import_file_parser (lambda_.Function): Lambda function that handles file parsing

    Args:
        scope (Construct): The scope in which to define this construct
        construct_id (str): The scoped construct ID
        bucket_name (str): Name of the existing S3 bucket to process files from
        **kwargs: Arbitrary keyword arguments passed to parent Stack class
    """

    def __init__(self, scope: Construct, construct_id: str, bucket_name: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Reference an existing S3 bucket using its name
        bucket = s3.Bucket.from_bucket_name(self, 'ImportBucket',
                                            bucket_name=bucket_name)

        queue = sqs.Queue.from_queue_attributes(
            self,
            "CatalogItemsQueue",
            queue_arn="arn:aws:sqs:eu-west-1:288761740770:ProductServiceStackCatalogBatchProcessF03-CatalogItemsQueueB3B6CE23-4hMqPokXval1",
            queue_url="https://eu-west-1.queue.amazonaws.com/288761740770/ProductServiceStackCatalogBatchProcessF03-CatalogItemsQueueB3B6CE23-4hMqPokXval1"
        )

        # Create Lambda function
        self.import_file_parser = lambda_.Function(
            self,
            'ImportFileParser',
            runtime=lambda_.Runtime.PYTHON_3_12,
            handler='import_file_parser.handler',
            code=lambda_.Code.from_asset('import_service/lambda_func/'),
            environment={'BUCKET_NAME': bucket.bucket_name,
                         "QUEUE_URL": queue.queue_url}
        )

        # Grant permissions to the Lambda function:
        bucket.grant_read_write(self.import_file_parser)
        bucket.grant_put(self.import_file_parser)
        bucket.grant_delete(self.import_file_parser)

        # Notifying lambda in case of new file appeared
        notification = s3_notifications.LambdaDestination(
            self.import_file_parser)

        bucket.add_event_notification(s3.EventType.OBJECT_CREATED,
                                      notification,
                                      s3.NotificationKeyFilter(prefix='uploaded/'))

        queue.grant_send_messages(self.import_file_parser)
