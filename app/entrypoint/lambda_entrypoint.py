import boto3
import logging
import json
import re


def handler(event, context):
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    lambda_client = boto3.client('lambda')

    link = event['queryStringParameters']['link']
    
    if re.match(
        r'[http|https\:\/\/]?[a-zA-Z0-9\.\/\?\:@\-_=#]+\.[a-zA-Z]{2,6}[a-zA-Z0-9\.\&\/\?\:@\-_=#]*',
            link) is None:

        logger.error("ERROR: Invalid URL")
        return {
            'statusCode': 500,
            'body': json.dumps('Invalid URL')
        }

    msg = {"link": link}
    logger.info("Get Link: %s", link)

    invoke_response = lambda_client.invoke(FunctionName="crawler-feature-generation",
                                           Payload=json.dumps(msg))
    logger.info(invoke_response)
    if invoke_response['StatusCode'] == 200:
        return json.loads(invoke_response['Payload'].read().decode('utf-8'))