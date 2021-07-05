import lambda_predict
import io
import json
from unittest.mock import patch

class Model():
    def predict(self, features):
        return 2

@patch('lambda_predict.os')
@patch('lambda_predict.boto3')
@patch('lambda_predict.joblib')
def test_get_model(mock_joblib, mock_boto3, mock_os):
    mock_os.environ.__getitem__.side_effect = ['MODEL', 'BUCKET']
    mock_joblib.load.return_value = True
    response = lambda_predict.get_model()
    assert response

    mock_os.environ.__getitem__.side_effect = ['MODEL', 'BUCKET']
    mock_joblib.load.side_effect = Exception()
    response = lambda_predict.get_model()
    assert response == ''


@patch('lambda_predict.get_model')
def test_handler_model_empty(mock_get_model):
    mock_get_model.return_value = ''
    event = {'body': '{"link": "https://www.google.com"}'}
    response = lambda_predict.handler(event, None)
    assert response['statusCode'] == 500

@patch('lambda_predict.os')
@patch('lambda_predict.boto3')
@patch('lambda_predict.get_model')
def test_handler_wrong_url(mock_get_model, mock_boto3, mock_os):
    mock_get_model.return_value = 'model'
    mock_os.environ.__getitem__.return_value = 'tablename'
    event = {'body': '{"link": "#"}'}
    response = lambda_predict.handler(event, None)
    assert response['statusCode'] == 400

@patch('lambda_predict.os')
@patch('lambda_predict.boto3')
@patch('lambda_predict.get_model')
def test_handler_new_link(mock_get_model, mock_boto3, mock_os):
    mock_get_model.return_value = Model()
    mock_os.environ.__getitem__.return_value = 'tablename'
    mock_boto3.client().query.return_value = {'Items': []}
    mock_boto3.client().invoke.return_value = {
                                                'StatusCode': 200,
                                                'Payload': io.BytesIO(b'{"features": {"feature1": "2"}}')
                                              }
    event = {'body': '{"link": "https://www.google.com"}'}
    response = lambda_predict.handler(event, None)
    assert response['statusCode'] == 200
    assert json.loads(response['body']) == {'link': 'https://www.google.com', 'appearances': 2}
    mock_boto3.client().invoke.assert_called_once()
    mock_boto3.client().query.assert_called_once()


@patch('lambda_predict.os')
@patch('lambda_predict.boto3')
@patch('lambda_predict.get_model')
def test_handler_old_link(mock_get_model, mock_boto3, mock_os):
    mock_get_model.return_value = Model()
    mock_os.environ.__getitem__.return_value = 'tablename'
    mock_boto3.client().query.return_value = {'Items': [{'appearances': {'N': '3'}}]}
    event = {'body': '{"link": "https://www.google.com"}'}
    response = lambda_predict.handler(event, None)
    assert response['statusCode'] == 200
    assert json.loads(response['body']) == {'link': 'https://www.google.com', 'appearances': 3}
    mock_boto3.client().invoke.assert_not_called()
    mock_boto3.client().query.assert_called_once()
