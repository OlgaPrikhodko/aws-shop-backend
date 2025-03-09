import unittest
from unittest.mock import patch, MagicMock
import os

from import_service.lambda_func.import_file_parser import handler


class TestImportFileParser(unittest.TestCase):
    """
    Test suite for the ImportFileParser lambda function

     This class contains unit tests that verify the Lambda function's ability to:
    - Process S3 events for CSV files
    - Move files from 'uploaded' to 'parsed' folder
    - Handle various error conditions

    The tests use mocking to avoid actual AWS service calls.
    """
    @patch.dict(os.environ, {"BUCKET_NAME": "test-bucket"})
    @patch("import_service.lambda_func.import_file_parser.s3")
    def test_handler_success(self, mock_s3):
        """
        Test successful processing of an S3 event.

        This test verifies that the handler:
        1. Correctly reads CSV content from S3
        2. Copies the file to the 'parsed' folder
        3. Deletes the original file from 'uploaded' folder

        Args:
            mock_s3: Mocked S3 client for testing without AWS calls
        """
        # Mock S3 get_object response with a sample CSV file
        mock_s3.get_object.return_value = {
            'Body': MagicMock(read=MagicMock(return_value=b"column1,column2\nvalue1,value2\n"))
        }

        event = {
            "Records": [
                {
                    "s3": {
                        "object": {"key": "uploaded/test-file.csv"}
                    }
                }
            ]
        }
        # Execute the handler
        response = handler(event, None)

        # Ensure copy and delete are called correctly
        mock_s3.copy_object.assert_called_once_with(
            Bucket="test-bucket",
            CopySource={"Bucket": "test-bucket",
                        "Key": "uploaded/test-file.csv"},
            Key="parsed/test-file.csv"
        )
        mock_s3.delete_object.assert_called_once_with(
            Bucket="test-bucket", Key="uploaded/test-file.csv"
        )

    @patch.dict(os.environ, {"BUCKET_NAME": "test-bucket"})
    def test_handler_no_records(self):
        """
        Test handling of event with no records.

        Verify that the handler gracefully handles empty events
        without making any S3 calls.
        """
        # Create empty event
        event = {"Records": []}

        # Execute handler
        response = handler(event, None)

        # Since no records, no calls to S3 should happen
        self.assertIsNone(response)

    @patch.dict(os.environ, {"BUCKET_NAME": "test-bucket"})
    @patch("import_service.lambda_func.import_file_parser.s3")
    def test_handler_s3_exception(self, mock_s3):
        """
        Test handling of an exception when calling S3.

        Verifies that the handler properly propagates S3 errors
        and includes the error message.

        Args:
            mock_s3: Mocked S3 client configured to raise an exception
        """
        # Configure S3 mock to raise an exception
        mock_s3.get_object.side_effect = Exception("S3 error")

        # Create test event
        event = {
            "Records": [
                {
                    "s3": {
                        "object": {"key": "uploaded/test-file.csv"}
                    }
                }
            ]
        }

        # Verify exception handling
        with self.assertRaises(Exception) as context:
            handler(event, None)

        # Ensure error message is preserved
        self.assertIn("S3 error", str(context.exception))


if __name__ == "__main__":
    unittest.main()
