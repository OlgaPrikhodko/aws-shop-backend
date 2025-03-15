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
    def __init__(self, scope: Construct, construct_id: str, environment: dict, **kwargs):
        super().__init__(scope, construct_id, **kwargs)

        # SQS implementation
        catalog_items_queue = sqs.Queue(
            self,
            "CatalogItemsQueue"
        )

        event_source = lambda_event_sources.SqsEventSource(
            catalog_items_queue, batch_size=5)

        create_product_topic = sns.Topic(
            self, "CreateProductTopic", topic_name="create_product_topic")

        create_product_topic.add_subscription(
            sns_subscriptions.EmailSubscription("ggg.poletaem@gmail.com"))

        environment["SNS_TOPIC_ARN"] = create_product_topic.topic_arn

        # Create Lambda function
        self.catalog_batch_process = lambda_.Function(
            self, "CatalogBatchProcess",
            runtime=lambda_.Runtime.PYTHON_3_12,
            code=lambda_.Code.from_asset("product_service/lambda_func/"),
            handler="catalog_batch.handler",
            environment=environment,
        )

        # SQS policy
        self.catalog_batch_process.add_event_source(event_source)
        catalog_items_queue.grant_consume_messages(
            self.catalog_batch_process)

        # SNS policy
        create_product_topic.grant_publish(self.catalog_batch_process)
