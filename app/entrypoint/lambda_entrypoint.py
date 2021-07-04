import boto3
import logging
import json

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


def handler(event, context):
    lambda_client = boto3.client('lambda')

    link = event['queryStringParameters']['link']
    msg = {"link": link}

    invoke_response = lambda_client.invoke(FunctionName="crawler-feature-generation",
                                           Payload=json.dumps(msg))
    print(invoke_response)
    if invoke_response['StatusCode'] == 200:
        return invoke_response['Payload'].read().decode('utf-8')