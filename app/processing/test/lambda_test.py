import lambda_processing
import requests
from unittest.mock import patch

def test_crawler_init():
    # Test default arg
    query_url = 'https://www.google.com'
    c = lambda_processing.Crawler(query_url)
    assert c.query_url == query_url
    assert c.visited_urls == []

    # Test passing value to default arg
    query_url = 'https://www.google.com'
    visited = ['https://www.amazon.com']
    c = lambda_processing.Crawler(query_url, visited)
    assert c.query_url == query_url
    assert c.visited_urls == visited

@patch('lambda_processing.requests')
def test_download_url(mock_requests):
    mock_requests.get().text = 'HTML'

    query_url = 'https://www.google.com'
    c = lambda_processing.Crawler(query_url)

    assert c.download_url(query_url) == 'HTML'

def test_run():
    query_url = 'https://www.google.com'
    c = lambda_processing.Crawler(query_url)
    return True
