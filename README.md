# AWS Shop Backend

A microservices-based backend implementation for an AWS shop application, built with serverless architecture.

## Overview

This project implements a serverless e-commerce backend using AWS services including Lambda, API Gateway, and more. The frontend repository can be found [here](https://github.com/OlgaPrikhodko/nodejs-aws-shop-react).

## Architecture

The application is built using a microservices architecture with the following components:

### Services

- **Product Service**: Manages product catalog (Lambda + API Gateway)
<!-- - **Authorization Service**: Handles user authentication and authorization
- **Import Service**: Manages product import operations
- **Cart Service**: Handles shopping cart operations -->

## API Endpoints

### Product Service
Base URL: https://6krhhlmu2l.execute-api.eu-west-1.amazonaws.com/prod

Available endpoints:
- GET `/products` - Retrieve all products
- GET `/products/{id}` - Retrieve specific product by ID
- POST `/products` - Create new product

### Lambda Functions

#### catalogBatchProcess
- Triggered by SQS events from catalogItemsQueue
- Processes messages in batches of 5
- Creates products in DynamoDB based on received messages
- Publishes notifications to SNS topic after product creation
- Environment variables required:
  - SNS_TOPIC_ARN: ARN of createProductTopic
  
## Import Service
Base URL: https://hr83sjmjyj.execute-api.eu-west-1.amazonaws.com/prod

### Available Endpoints:
- GET `/import` - Generate signed URL for CSV file upload
  - Query Parameters:
    - `name` (required): Name of the CSV file to upload
  - Response: Signed URL as string
  - Example: `/import?name=products.csv`

### Usage Example:
```
# Get signed URL for file upload
curl "https://hr83sjmjyj.execute-api.eu-west-1.amazonaws.com/prod/import?name=products.csv"

```

### CSV File Requirements:
- Format: CSV file with product data
- Expected columns:
  - id
  - title
  - description
  - price
  - count

### Infrastructure (CDK Stack)

#### SQS Configuration
- Queue name: catalogItemsQueue
- Batch size: 5 messages
- Configured as event source for catalogBatchProcess lambda

#### SNS Configuration
- Topic name: createProductTopic
- Email subscription for product creation notifications
- Optional: Filter policy configuration for routing messages based on product attributes

### IAM Permissions
The following permissions are configured in the CDK stack:
- catalogBatchProcess lambda permissions:
  - SQS: ReceiveMessage, DeleteMessage
  - SNS: Publish
  - DynamoDB: Required permissions for product creation

### Import Process Flow:
1. CSV files uploaded to S3 'uploaded/' directory
2. importFileParser processes files and sends records to SQS
3. catalogBatchProcess receives messages in batches
4. New products are created in DynamoDB
5. Notifications sent via SNS
6. Subscribers receive emails based on filter policies (if configured)
4. System will process the file and import products


### Lambda Functions

### importProductsFile 
- Generates signed URLs for file upload

#### importFileParser
- Processes CSV files uploaded to the S3 bucket
- Reads records from CSV files and sends them to SQS queue (catalogItemsQueue)
- Moves processed files from 'uploaded/' to 'parsed/' directory
- Environment variables:
  - BUCKET_NAME: S3 bucket name
  - QUEUE_URL: SQS queue URL

### Infrastructure (CDK Stack)

#### SQS Configuration
- Queue name: catalogItemsQueue
- Batch size: 5 messages
- Configured as event source for catalogBatchProcess lambda

#### SNS Configuration
- Topic name: createProductTopic
- Email subscription for product creation notifications
- Optional: Filter policy configuration for routing messages based on product attributes

### IAM Permissions
The following permissions are configured in the CDK stack:
- catalogBatchProcess lambda permissions:
  - SQS: ReceiveMessage, DeleteMessage
  - SNS: Publish
  - DynamoDB: Required permissions for product creation


## Frontend Shop App Link:

[https://d2qer9nz6tkkfj.cloudfront.net/](https://d2qer9nz6tkkfj.cloudfront.net/)

Example for creating product:
```
curl -X POST https://6krhhlmu2l.execute-api.eu-west-1.amazonaws.com/prod/products \
-H "Content-Type: application/json" \
-d '{
    "title": "New Product",
    "description": "Product description",
    "price": 99.99,
    "count": 100
}'
```

## Project Structure

```
.
├── backend
│   ├── authorization_service    # auth service repo
│   ├── import_service          # import service repo
│   └── product_service         # product service repo
├── cart_service                # cart service repo
│   └── nodejs-aws-cart-api
└── frontend                    # frontend repo
```


### Schemas for products and stocks databases (DynamoDB):

Product model:

```
  products:
    id -  uuid (Primary key)
    title - text, not null
    description - text
    price - integer
```

Stock model:

```
  stocks:
    product_id - uuid (Foreign key from products.id)
    count - integer (Total number of products in stock, can't be exceeded)
```

## Technical Stack

- **Runtime**: Python 3.9+
- **Infrastructure**: AWS CDK
- **Services**:
  - AWS Lambda
  - API Gateway
  - Amazon DynamoDB


### Prerequisites

1. AWS CLI installed and configured
2. AWS CDK installed
3. Python 3.9 or higher

### Deployment

Each service contains its own:
- Infrastructure as Code (IaC)
- Business logic implementation
- Test suites
- Service-specific documentation



