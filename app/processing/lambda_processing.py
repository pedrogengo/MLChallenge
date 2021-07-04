import logging
import requests
import json
import boto3
import os
from urllib.parse import urljoin
from bs4 import BeautifulSoup


class Crawler:
    """A crawler allows us to enter a link and obtain information about it.
    
    With Crawler we can pass a URL and find other URLs that are referenced in it.

    Attributes:
        query_url: An URL to find linked urls.
        visited_urls: A list containing URLs that we already have in our
        database.
    """

    def __init__(self, url):
        # self.visited_urls = visited_urls
        self.urls_to_visit = []
        self.query_url = url

    def download_url(self, url):
        return requests.get(url).text

    def get_linked_urls(self, url, html):
        paths = []
        soup = BeautifulSoup(html, 'html.parser')
        for link in soup.find_all('a'):
            path = link.get('href')
            if path:
                if path.startswith('/'):
                    path = urljoin(url, path)
                paths.append(path)
        return paths

    # def add_url_to_visit(self, url):
    #     if url not in self.visited_urls and url not in self.urls_to_visit:
    #         self.urls_to_visit.append(url)

    def crawl(self, url):
        html = self.download_url(url)
        for url in self.get_linked_urls(url, html):
            self.urls_to_visit.append(url)

    def run(self):
        url = self.query_url
        logging.info(f'Crawling: {url}')
        try:
            self.crawl(url)
        except Exception:
            logging.exception(f'Failed to crawl: {url}')

def get_visited_urls(client, tablename):
    response = client.Table(TableName=tablename)
    data = response['Items']
    while 'LastEvaluatedKey' in response:
        response = client.scan(TableName=tablename,
                               ExclusiveStartKey=response['LastEvaluatedKey'])
        data.extend(response['Items'])
    
    if len(data) > 0:
        visited_urls = [item['link']['S'] for item in data]
    else:
        visited_urls = []
    return visited_urls

def create_dynamo_item(client, tablename, link, appearances):
    response = client.put_item(
            TableName=tablename,
            Item={
                'link': {
                    'S': link,
                },
                'appearances': {
                    'N': str(appearances)
                }
            }
        )
    return response

def update_appearances(client, table, link, appearances):

    response = client.update_item(
        TableName=table,
        Key={
            'link': {
                'S': link,
            }
        },
        UpdateExpression='set appearances=appearances + :f',
        ExpressionAttributeValues={
            ':f': {'N': appearances}
        },
        ReturnValues='UPDATED_NEW'
    )
    return response

def handler(event, context):
    client = boto3.client('dynamodb')
    sqs = boto3.client("sqs")
    tablename = os.environ['TABLE_NAME']
    queue_url = os.environ["QUEUE_URL"]

    visited_urls = get_visited_urls(client, tablename)

    record = event["Records"][0]
    body = json.loads(record['body'])
    depth = body['Depth']
    query_url = body['Link']
    
    crawler = Crawler(query_url, visited_urls=visited_urls)
    crawler.run()
    references = crawler.urls_to_visit

    # primeiro inserir minha url no RDS com appearence 0
    create_dynamo_item(client, tablename, query_url, 0)

    # depois passar por references e se nao existir no visited_urls, crio com appearence 1
    for link in references:
        if link in visited_urls:
            update_appearances(client, tablename, link, 1)
        else:
            create_dynamo_item(client, tablename, link, 1)
    if depth == 0:
        body = {
            'query_url': query_url,
            'depth': depth,
            'details': 'Done'
        }
    else:
        # queue_url = sqs.get_queue_url(QueueName=queue_name).get('QueueUrl')
        # logger.debug("Queue URL is %s", queue_url)

        # Sending entries to sqs
        try:
            message_body = f'{{"Link": "{link}", "Depth": {depth-1}}}'
            resp = sqs.send_message(QueueUrl=queue_url, MessageBody=message_body)
            # logger.debug("Send result: %s", resp)
            body = {
                'query_url': query_url,
                'depth': depth-1,
                'details': 'Going deeper'
            }

        except Exception as e:
            return {
                'statusCode': 500,
                'body': json.dumps(str(e))
            }

    return {
            'statusCode': 200,
            'body': json.dumps(body)
        }