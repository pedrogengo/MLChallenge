import lambda_entrypoint
import io
from unittest.mock import patch

@patch('lambda_entrypoint.boto3')
def test_handler(mock_boto3):
    mock_boto3.client().invoke.return_value = {
        'StatusCode': 200,
        'Payload': io.BytesIO(b'{"mock": "Mock"}')}

    event = {"queryStringParameters": {"link": "https://www.google.com"}}
    response = lambda_entrypoint.handler(event, None)
    assert response == {'mock': 'Mock'}

    mock_boto3.client().invoke.return_value = {
        'StatusCode': 200,
        'Payload': io.BytesIO(b'{"mock": "Mock"}')}

    event = {"queryStringParameters": {"link": ""}}
    response = lambda_entrypoint.handler(event, None)
    assert response['statusCode'] == 500