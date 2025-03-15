from aws_cdk import (
    Stack,
    aws_lambda as lambda_,
    aws_sqs as sqs,
    aws_lambda_event_sources as lambda_event_sources)

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
