import logging
import requests
import json
import boto3
import os
import re
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
            if re.match(
                r'[http|https\:\/\/]?[a-zA-Z0-9\.\/\?\:@\-_=#]+\.[a-zA-Z]{2,6}[a-zA-Z0-9\.\&\/\?\:@\-_=#]*',
                    path):
                paths.append(path)
        return paths

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
    response = client.scan(TableName=tablename)
    data = response['Items']
    while 'LastEvaluatedKey' in response:
        response = client.scan(TableName=tablename,
                               ExclusiveStartKey=response['LastEvaluatedKey'])
        data.extend(response['Items'])
    
    if len(data) > 0:
        visited_urls = [item['link']['S'] for item in data if item.get('appearances')]
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
            ':f': {'N': str(appearances)}
        },
        ReturnValues='UPDATED_NEW'
    )
    return response

def handler(event, context):

    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    logger.info("Event: %s", event)

    client = boto3.client('dynamodb')
    sqs = boto3.client("sqs")
    lambda_client = boto3.client('lambda')
    tablename = os.environ['TABLE_NAME']
    queue_url = os.environ["QUEUE_URL"]

    record = event["Records"][0]
    body = json.loads(record['body'])
    depth = int(body['Depth'])
    query_url = body['Link']

    if re.match(
        r'[http|https\:\/\/]?[a-zA-Z0-9\.\/\?\:@\-_=#]+\.[a-zA-Z]{2,6}[a-zA-Z0-9\.\&\/\?\:@\-_=#]*',
            query_url) is None:

        logger.error("ERROR: Invalid URL")
        return {
            'statusCode': 400,
            'body': json.dumps('Invalid URL')
        }
 
    visited_urls = get_visited_urls(client, tablename)
    logger.info("Visited URLs: %s", visited_urls)

    logger.info("Running Crawler")
    crawler = Crawler(query_url)
    crawler.run()
    references = crawler.urls_to_visit
    logger.info("URLs to visit: %s", references)

    if query_url not in visited_urls:
        # Insert my link in Dynamo with  appearence 0
        create_dynamo_item(client, tablename, query_url, 0)
        lambda_client.invoke(FunctionName="crawler-feature-generation",
                                            InvocationType='Event',
                                            Payload=json.dumps({'link': query_url}))
    logger.info("Created query link in dynamo")

    # Iterate over refrences and, if doesnt exists inside visited_urls, create with appearence 1
    for link in references:
        if link in visited_urls:
            update_appearances(client, tablename, link, 1)
        else:
            create_dynamo_item(client, tablename, link, 1)
            lambda_client.invoke(FunctionName="crawler-feature-generation",
                                          InvocationType='Event',
                                           Payload=json.dumps({'link': link}))
    logger.info("Updated appearances")

    if depth == 0:
        body = {
            'query_url': query_url,
            'depth': depth,
            'details': 'Done'
        }
    else:

        # Sending entries to sqs
        try:
            next_links = list(set(references) - set(visited_urls))
            i = 0

            # We need to apply this because the method send_message_batch has a limit of 10 entries
            for i in range(int(len(next_links)//10)):
                sqs_entries = [{'Id': str(i), 'MessageBody': f'{{"Link": "{link}", "Depth": {depth - 1}}}'}
                            for i, link in enumerate(next_links[(i*10):(10*(i+1))])]
                resp = sqs.send_message_batch(QueueUrl=queue_url, Entries=sqs_entries)
                logger.info("Send result: %s", resp)

            # In case of len(next_link) < 10
            if i == 0:
                i = -1

            sqs_entries = [{'Id': str(i), 'MessageBody': f'{{"Link": "{link}", "Depth": {depth - 1}}}'}
                            for i, link in enumerate(next_links[(10*(i+1)):])]
            resp = sqs.send_message_batch(QueueUrl=queue_url, Entries=sqs_entries)
            logger.info("Send result: %s", resp)

            body = {
                'next_urls': next_links,
                'depth': depth-1,
                'details': 'Going deeper'
            }

        except Exception as e:
            logger.error("ERROR: %s", str(e))
            return {
                'statusCode': 500,
                'body': json.dumps(str(e))
            }

    return {
            'statusCode': 200,
            'body': json.dumps(body)
        }
