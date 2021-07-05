import lambda_processing
import json
from unittest.mock import patch

def test_crawler_init():
    # Test default arg
    query_url = 'https://www.google.com'
    c = lambda_processing.Crawler(query_url)
    assert c.query_url == query_url

@patch('lambda_processing.requests')
def test_crawler_download_url(mock_requests):
    mock_requests.get().text = 'HTML'

    query_url = 'https://www.google.com'
    c = lambda_processing.Crawler(query_url)

    assert c.download_url(query_url) == 'HTML'

@patch('lambda_processing.BeautifulSoup')
def test_crawler_get_linked_urls(mock_bs):
    mock_bs().find_all.return_value = [{'href': 'https://www.google.com'},
                            {'href': '#'},
                            {'href': '/test'}]
    c = lambda_processing.Crawler('https://www.test.com')
    response = c.get_linked_urls('https://www.test.com', None)
    assert response == ['https://www.google.com', 'https://www.test.com/test']

@patch('lambda_processing.BeautifulSoup')
@patch('lambda_processing.requests')  
def test_crawler_run(mock_requests, mock_bs):
    mock_bs().find_all.return_value = [{'href': 'https://www.google.com/2'},
                                       {'href': '#'},
                                       {'href': '/test'}]
    mock_requests.get().text = 'HTML'
    query_url = 'https://www.google.com'
    c = lambda_processing.Crawler(query_url)
    c.run()
    assert c.urls_to_visit == ['https://www.google.com/2', 'https://www.google.com/test']

@patch('lambda_processing.boto3')
def test_get_visited_urls(mock_boto3):
    mock_boto3.scan.return_value = {'Items': [{'link': {'S': 'site1'}}, {'link': {'S': 'site2'}}]}
    response = lambda_processing.get_visited_urls(mock_boto3, 'name')
    assert response == ['site1', 'site2']

    mock_boto3.scan.return_value = {'Items': []}
    response = lambda_processing.get_visited_urls(mock_boto3, 'name')
    assert response == []

    mock_boto3.scan.side_effect = [{'Items': [{'link': {'S': 'site1'}}, {'link': {'S': 'site2'}}], 'LastEvaluatedKey': True},
                                   {'Items': [{'link': {'S': 'site3'}}, {'link': {'S': 'site4'}}]}]
    response = lambda_processing.get_visited_urls(mock_boto3, 'name')
    assert response == ['site1', 'site2', 'site3', 'site4']

@patch('lambda_processing.os')
@patch('lambda_processing.boto3')
def test_handler_wrong_url(mock_boto3, mock_os):
    mock_os.environ.__getitem__.side_effect = ['tablename', 'queue_url']
    event = {'Records': [{'body': '{"Depth": 1, "Link": "#"}'}]}
    response = lambda_processing.handler(event, None)
    assert response['statusCode'] == 400

@patch('lambda_processing.os')
@patch('lambda_processing.boto3')
@patch('lambda_processing.Crawler')
@patch('lambda_processing.create_dynamo_item')
@patch('lambda_processing.update_appearances')
def test_handler_depth_0(mock_update, mock_create, mock_crawler, mock_boto3, mock_os):
    mock_os.environ.__getitem__.side_effect = ['tablename', 'queue_url']
    mock_boto3.client().scan.return_value = {'Items': [{'link': {'S': 'site1'}}, {'link': {'S': 'site2'}}]}
    mock_crawler().urls_to_visit = ['site1', 'site3']
    event = {'Records': [{'body': '{"Depth": 0, "Link": "https://www.google.com"}'}]}
    response = lambda_processing.handler(event, None)
    assert response['statusCode'] == 200
    assert json.loads(response['body'])['depth'] == 0
    assert mock_create.call_count == 2
    mock_update.assert_called_once()

@patch('lambda_processing.os')
@patch('lambda_processing.boto3')
@patch('lambda_processing.Crawler')
@patch('lambda_processing.create_dynamo_item')
@patch('lambda_processing.update_appearances')
def test_handler_depth_gt_0_small(mock_update, mock_create, mock_crawler, mock_boto3, mock_os):
    mock_os.environ.__getitem__.side_effect = ['tablename', 'queue_url']
    mock_boto3.client().scan.return_value = {'Items': [{'link': {'S': 'site1'}}, {'link': {'S': 'site2'}}]}
    mock_crawler().urls_to_visit = ['site1', 'site3']
    event = {'Records': [{'body': '{"Depth": 2, "Link": "https://www.google.com"}'}]}
    response = lambda_processing.handler(event, None)
    assert response['statusCode'] == 200
    assert json.loads(response['body'])['depth'] == 1
    assert json.loads(response['body'])['next_urls'] == ['site3']
    assert mock_create.call_count == 2
    assert mock_boto3.client().invoke.call_count == 2
    mock_update.assert_called_once()
    mock_boto3.client().send_message_batch.assert_called_once()

@patch('lambda_processing.os')
@patch('lambda_processing.boto3')
@patch('lambda_processing.Crawler')
@patch('lambda_processing.create_dynamo_item')
@patch('lambda_processing.update_appearances')
def test_handler_depth_gt_0_small(mock_update, mock_create, mock_crawler, mock_boto3, mock_os):
    mock_os.environ.__getitem__.side_effect = ['tablename', 'queue_url']
    mock_boto3.client().scan.return_value = {'Items': [{'link': {'S': 'site1'}}, {'link': {'S': 'site2'}}]}
    mock_crawler().urls_to_visit = ['site1', 'site3', 's4', 's5', 's6', 's7', 's8', 's9', 's0', 's10', 's11', 's12']
    event = {'Records': [{'body': '{"Depth": 2, "Link": "https://www.google.com"}'}]}
    response = lambda_processing.handler(event, None)
    assert response['statusCode'] == 200
    assert json.loads(response['body'])['depth'] == 1
    assert sorted(json.loads(response['body'])['next_urls']) == sorted(['site3', 's4', 's5', 's6', 's7', 's8', 's9', 's0', 's10', 's11', 's12'])
    assert mock_create.call_count == 12
    assert mock_boto3.client().invoke.call_count == 12
    mock_update.assert_called_once()
    assert mock_boto3.client().send_message_batch.call_count == 2
