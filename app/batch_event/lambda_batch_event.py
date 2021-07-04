import boto3
import logging
import os
import json

def get_environment_variables():
    queue_url = os.environ["QUEUE_URL"]
    depth = os.environ['DEPTH']
    bucket = os.environ['BUCKET']
    return queue_url, bucket, depth

def handler(event, context):
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    # Start clients
    s3 = boto3.client('s3')
    sqs = boto3.client("sqs")

    queue_url, bucket, depth = get_environment_variables()

    # Getting the content of csv inside s3 bucket
    try:
        query_table = event['Records'][0]['s3']['object']['key']

    except KeyError:
        logger.error('ERROIntegration error with S3. Try again later')
        return {
            'statusCode': 500,
            'body': json.dumps('Integration error with S3. Try again later')
        }
    
    csv_response = s3.get_object(Bucket=bucket, Key=query_table)
    csv_reader = csv_response['Body'].read().decode('utf-8').split('\r\n')

    # Retrieve the queue url, in order to use sqs api
    logger.info("Queue URL is %s", queue_url)

    # Sending entries to sqs
    try:
        # Creating the list to send in batch format for sqs
        i = 0

        # We need to apply this because the method send_message_batch has a limit of 10 entries
        for i in range(int(len(csv_reader)//10)):
            sqs_entries = [{'Id': str(j), 'MessageBody': f'{{"Link": "{link}", "Depth": {depth}}}'}
                        for j, link in enumerate(csv_reader[(i*10):(10*(i+1))])]
            resp = sqs.send_message_batch(QueueUrl=queue_url, Entries=sqs_entries)
            logger.info("Send result: %s", resp)
        
        # In case of len(next_link) < 10
        if i == 0:
            i = -1

        sqs_entries = [{'Id': str(j), 'MessageBody': f'{{"Link": "{link}", "Depth": {depth}}}'}
                        for j, link in enumerate(csv_reader[(10*(i+1)):])]
        resp = sqs.send_message_batch(QueueUrl=queue_url, Entries=sqs_entries)
        logger.info("Send result: %s", resp)

        return {
            'statusCode': 200,
            'body': json.dumps('Done!')
        }

    except Exception as e:
        logger.error("Got error: %s", str(e))
        return {
            'statusCode': 500,
            'body': json.dumps(str(e))
        }
