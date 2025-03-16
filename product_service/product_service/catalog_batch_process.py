from aws_cdk import (
    Stack,
    aws_lambda as lambda_,
    aws_sqs as sqs,
    aws_lambda_event_sources as lambda_event_sources,
    aws_sns as sns,
    aws_sns_subscriptions as sns_subscriptions
)

from constructs import Construct


class CatalogBatchProcess(Stack):
    """
    AWS CDK Stack for catalog batch processing infrastructure.

    This stack creates:
    - SQS Queue for receiving product data
    - SNS Topic for notifications with filtered subscriptions
    - Lambda function for processing the data
    - Necessary IAM permissions and event sources
    """

    def __init__(self, scope: Construct, construct_id: str, environment: dict, **kwargs):
        super().__init__(scope, construct_id, **kwargs)

        # Create SQS Queue for receiving product data
        catalog_items_queue = sqs.Queue(
            self,
            "CatalogItemsQueue",
            queue_name='CatalogItemsQueue'
        )

        # Configure SQS as event source for Lambda
        event_source = lambda_event_sources.SqsEventSource(
            catalog_items_queue, batch_size=5)

        # Create SNS Topic for notifications
        create_product_topic = sns.Topic(
            self, "CreateProductTopic", topic_name="create_product_topic")

        # Add email subscription for all products (no filter)
        create_product_topic.add_subscription(
            sns_subscriptions.EmailSubscription("ggg.poletaem@gmail.com"))

        # Add filtered subscription for expensive products (price > 100)
        create_product_topic.add_subscription(
            sns_subscriptions.EmailSubscription(
                "helga.prikhodko@gmail.com",
                filter_policy={
                    "price": sns.SubscriptionFilter.numeric_filter(
                        greater_than=30
                    )
                }
            )
        )

        # Add SNS Topic ARN to Lambda environment variables
        environment["SNS_TOPIC_ARN"] = create_product_topic.topic_arn

        # Create Lambda function for processing catalog items
        self.catalog_batch_process = lambda_.Function(
            self, "CatalogBatchProcess",
            runtime=lambda_.Runtime.PYTHON_3_12,
            code=lambda_.Code.from_asset("product_service/lambda_func/"),
            handler="catalog_batch.handler",
            environment=environment,
        )

        # SQS policy
        # Grant Lambda permission to consume messages from SQS
        self.catalog_batch_process.add_event_source(event_source)
        catalog_items_queue.grant_consume_messages(
            self.catalog_batch_process)

        # SNS policy
        # Grant Lambda permission to publish to SNS
        create_product_topic.grant_publish(self.catalog_batch_process)
