# AWS Shop Backend

Microservices backend for the AWS shop application.

Frontend - [Repository](https://github.com/OlgaPrikhodko/nodejs-aws-shop-react)

## Services

Working tree should look somehow like this:
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

### Product Service

- Manages product catalog
- API Gateway + Lambda implementation

## Development

### Prerequisites

- Python 3.9+
- AWS CDK
- AWS CLI

## Service Structure

Each service is a separate CDK application with its own:

- Infrastructure as Code
- Business Logic
- Tests
- Documentation
