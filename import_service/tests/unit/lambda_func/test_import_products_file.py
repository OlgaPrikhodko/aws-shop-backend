import os
import unittest
from unittest.mock import patch

from import_service.lambda_func.import_products_file import handler


class TestImportProductsFile(unittest.TestCase):
    """
    Test suite for import_products_file lambda function

    Unit tests for verifying the behavior of lambda function
    that generates presigned URLs for S3 file uploads
    """

    # Mock environment variable
    @patch.dict(os.environ, {"BUCKET_NAME": "test-bucket"})
    @patch("import_service.lambda_func.import_products_file.s3")  # Mock S3 client
    def test_handler_success(self, mock_s3):
        """
        Test if handler successfully returns a presigned URL.

        This test mocks the S3 client's generate_presigned_url method
        to simulate a successful S3 operation.
        It verifies that the handler under test returns a 200 status code
        and a presigned URL in the response body.

        Args:
            mock_s3: Mocked S3 client instance
        """
        # Mock presigned URL response
        mock_s3.generate_presigned_url.return_value = "https://signed-url.com"

        # Simulated API Gateway event with query params
        event = {"queryStringParameters": {"name": "test-file.csv"}}
        response = handler(event, None)

        # Assertions
        self.assertEqual(response["statusCode"], 200)
        self.assertIn("https://signed-url.com", response["body"])

    def test_handler_missing_filename(self):
        """
        Test if handler returns 400 when filename is missing.

        Verifies that the handler returns a 400 status code when
        the required 'name' parameter is missing from the request.

        """
        event = {"queryStringParameters": {}}  # No name key
        response = handler(event, None)

        # Assertions
        self.assertEqual(response["statusCode"], 400)
        self.assertIn("File name is required", response["body"])

    @patch.dict(os.environ, {"BUCKET_NAME": "test-bucket"})
    @patch("import_service.lambda_func.import_products_file.s3")
    def test_handler_s3_exception(self, mock_s3):
        """
        Test if handler returns 500 when S3 raises an exception.

        Args:
            mock_s3: Mocked S3 client instance
        """
        # Configure mock to raise an exception
        mock_s3.generate_presigned_url.side_effect = Exception("S3 error")

        # Create test event
        event = {"queryStringParameters": {"name": "test-file.csv"}}
        response = handler(event, None)

        # Assertions
        self.assertEqual(response["statusCode"], 500)
        self.assertIn("S3 error", response["body"])


if __name__ == "__main__":
    unittest.main()
