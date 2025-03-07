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



