import lambda_feature_generation
from unittest.mock import patch
import json

def test_link_class_ok():
    link = 'https://www.google.com' #len=22
    link_instance = lambda_feature_generation.Link(link)
    assert link_instance.url == link
    assert link_instance.feature1 == 22
    assert link_instance.feature2 == 2
    assert link_instance.feature3 == 4
    assert link_instance.feature4 == 0
    assert link_instance.feature5 == 0
    assert link_instance.feature6 == 17
    assert link_instance.feature7 == 0
    assert link_instance.feature8 == 3
    assert link_instance.feature9 == 11
    assert link_instance.feature10 == 3

def test_link_class_not_ok():
    link = '' #len=22
    link_instance = lambda_feature_generation.Link(link)
    assert link_instance.url == link
    assert link_instance.feature1 == 0
    assert link_instance.feature2 == 0
    assert link_instance.feature3 == 0
    assert link_instance.feature4 == 0
    assert link_instance.feature5 == 0
    assert link_instance.feature6 == 0
    assert link_instance.feature7 == 0
    assert link_instance.feature8 == 0
    assert link_instance.feature9 == 0
    assert link_instance.feature10 == 3

def test_update_features():
    pass

@patch('lambda_feature_generation.boto3')
@patch('lambda_feature_generation.os')
@patch('lambda_feature_generation.update_features')
def test_handler_new_url(mock_update_features, mock_os, mock_boto3):
    mock_os.__getitem__.return_value = 'tablename'
    # To enter in line 133
    mock_boto3.client().query.return_value = {'Items': []}
    mock_boto3.client().put_item.return_value = True

    response = lambda_feature_generation.handler({"link": "https://www.google.com"}, None)
    assert response['statusCode'] == 200
    assert json.loads(response['body'])['features'] == {
                                                            'feature1': 22,
                                                            'feature2': 2,
                                                            'feature3': 4,
                                                            'feature4': 0,
                                                            'feature5': 0,
                                                            'feature6': 17,
                                                            'feature7': 0,
                                                            'feature8': 3,
                                                            'feature9': 11,
                                                            'feature10': 3
                                                        }
    mock_boto3.client().put_item.assert_called_once()
    mock_update_features.assert_not_called()

@patch('lambda_feature_generation.boto3')
@patch('lambda_feature_generation.os')
@patch('lambda_feature_generation.update_features')
def test_handler_not_new_url(mock_update_features, mock_os, mock_boto3):
    mock_os.__getitem__.return_value = 'tablename'
    # To enter in line 150
    mock_boto3.client().query.return_value = {'Items': [{'features': {'M': {'feature1': {'N': 19}}}}]}

    response = lambda_feature_generation.handler({"link": "https://www.google.com"}, None)
    assert response['statusCode'] == 200
    assert json.loads(response['body'])['features'] == {
                                                            'feature1': 19,
                                                        }
    mock_boto3.client().put_item.assert_not_called()
    mock_update_features.assert_not_called()

@patch('lambda_feature_generation.boto3')
@patch('lambda_feature_generation.os')
@patch('lambda_feature_generation.update_features')
def test_handler_withou_features(mock_update_features, mock_os, mock_boto3):
    mock_os.__getitem__.return_value = 'tablename'
    # To enter in line 156
    mock_boto3.client().query.return_value = {'Items': [{'link': 'https://www.google.com'}]}
    mock_boto3.client().put_item.return_value = True

    response = lambda_feature_generation.handler({"link": "https://www.google.com"}, None)
    assert response['statusCode'] == 200
    assert json.loads(response['body'])['features'] == {
                                                            'feature1': 22,
                                                            'feature2': 2,
                                                            'feature3': 4,
                                                            'feature4': 0,
                                                            'feature5': 0,
                                                            'feature6': 17,
                                                            'feature7': 0,
                                                            'feature8': 3,
                                                            'feature9': 11,
                                                            'feature10': 3
                                                        }
    mock_boto3.client().put_item.assert_not_called()
    mock_update_features.assert_called_once()