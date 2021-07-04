import boto3
import logging
import os
import json

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

def get_environment_variables():
    queue_url = os.environ["QUEUE_URL"]
    depth = os.environ['DEPTH']
    bucket = os.environ['BUCKET']
    return queue_url, bucket, depth

def handler(event, context):
    # Start clients
    s3 = boto3.client('s3')
    sqs = boto3.client("sqs")

    queue_url, bucket, depth = get_environment_variables()

    # Getting the content of csv inside s3 bucket
    try:
        query_table = event['Records']['s3']['object']['key']

    except KeyError:
        return {
            'statusCode': 500,
            'body': json.dumps('Integration error with S3. Try again later')
        }
    
    csv_response = s3.get_object(Bucket=bucket, Key=query_table)
    csv_reader = csv_response['Body'].read().decode('utf-8').split('\n')

    # Creating the list to send in batch format for sqs
    sqs_entries = [{'Id': i, 'MessageBody': f'{{"Link": "{link}", "Depth": {depth}}}'}
                   for i, link in enumerate(csv_reader)]
    logger.debug('SQS Entries: %s', sqs_entries)

    # Retrieve the queue url, in order to use sqs api
    # queue_url = sqs.get_queue_url(QueueName=queue_name).get('QueueUrl')
    logger.debug("Queue URL is %s", queue_url)

    # Sending entries to sqs
    try:
        resp = sqs.send_message_batch(QueueUrl=queue_url, Entries=sqs_entries)
        logger.debug("Send result: %s", resp)
        return {
            'statusCode': 200,
            'body': json.dumps('Done!')
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps(str(e))
        }
