import lambda_batch_event
import io
from unittest.mock import patch

@patch('lambda_batch_event.os')
def test_get_environment_variables(mock_os):
    mock_os.environ.__getitem__.side_effect = ['queue_url', '7', 'bucketname']
    queue_url, bucket, depth = lambda_batch_event.get_environment_variables()
    assert queue_url == 'queue_url'
    assert bucket == 'bucketname'
    assert depth == '7'

@patch('lambda_batch_event.boto3')
@patch('lambda_batch_event.os')
def test_handler_first_exception(mock_os, mock_boto3):
    mock_os.environ.__getitem__.side_effect = ['queue_url', '7', 'bucketname']
    event = {'Records': [{'s3': {'key': '3'}}]}
    response = lambda_batch_event.handler(event, None)
    assert response['statusCode'] == 500
    assert response['body'] == '"Integration error with S3. Try again later"'

@patch('lambda_batch_event.boto3')
@patch('lambda_batch_event.os')
def test_handler_ok(mock_os, mock_boto3):
    mock_os.environ.__getitem__.side_effect = ['queue_url', '7', 'bucketname']
    mock_boto3.client().get_object.return_value = {'Body':  io.BytesIO(b'a\r\nb\r\n')}
    event = {'Records': [{'s3': {'object': {'key': 'inputs/link.csv'}}}]}
    response = lambda_batch_event.handler(event, None)
    assert response['statusCode'] == 200
    mock_boto3.client().send_message_batch.assert_called_once()

    mock_os.environ.__getitem__.side_effect = ['queue_url', '7', 'bucketname']
    mock_boto3.client().get_object.return_value = {
                                                'Body': io.BytesIO(b'a\r\nb\r\na\r\nb\r\na\r\n \
                                                         b\r\na\r\nb\r\na\r\nb\r\na\r\nb\r\n')
                                               }
    event = {'Records': [{'s3': {'object': {'key': 'inputs/link.csv'}}}]}
    response = lambda_batch_event.handler(event, None)
    assert response['statusCode'] == 200
    mock_boto3.client().send_message_batch.call_count == 2
