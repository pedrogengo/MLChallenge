import boto3
import logging
import os

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

QUEUE_NAME = os.getenv("QUEUE_NAME")
SQS = boto3.client("sqs")

def handler(event, context):

    data = event['body']

    queue_url = SQS.get_queue_url(QueueName=QUEUE_NAME).get('QueueUrl')
    logger.debug("Queue URL is %s", queue_url)

    logger.debug("Recording with event %s", event)
    try:
        logger.debug("Recording %s", data)
        resp = SQS.send_message(QueueUrl=queue_url, MessageBody=data)
        logger.debug("Send result: %s", resp)
        return 'ok'

    except Exception as e:
        raise Exception("Could not record link! %s" % e)