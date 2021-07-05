import joblib
import os
import boto3
import json
import re
from io import BytesIO


def get_model():
    # In order to prevent cold start
    model_name = os.environ['MODEL_NAME']
    bucket_name = os.environ['BUCKET_NAME']
    s3 = boto3.resource('s3')
    with BytesIO() as data:
        try:
            s3.Bucket(bucket_name).download_fileobj(model_name, data)
            data.seek(0)    # move back to the beginning after writing
            model = joblib.load(data)
        except Exception:
            model = ''
    return model

def handler(event, context):

    model = get_model()
    if model != '':
        lambda_client = boto3.client('lambda')
        dynamo = boto3.client('dynamodb')

        tablename = os.environ['TABLE_NAME']

        link = json.loads(event['body'])['link']

        # Verify if is a valid link
        if re.match(
            r'[http|https\:\/\/]?[a-zA-Z0-9\.\/\?\:@\-_=#]+\.[a-zA-Z]{2,6}[a-zA-Z0-9\.\&\/\?\:@\-_=#]*',
                link) is None:

            return {
                'statusCode': 400,
                'body': json.dumps('Invalid URL')
            }

        payload = {"link": link}

        # Verify if the link already exists in our database and have appearances
        dynamo_response = dynamo.query(
            ExpressionAttributeValues={
                ':v1': {
                    'S': link,
                },
            },
            KeyConditionExpression='link = :v1',
            TableName=tablename,
        )

        if len(dynamo_response['Items']) == 0 or dynamo_response['Items'][0].get('appearances') is None:
            # Getting features
            invoke_response = lambda_client.invoke(FunctionName="crawler-feature-generation",
                                            Payload=json.dumps(payload))
            decoded_response = json.loads(invoke_response['Payload'].read().decode('utf-8'))
            features = list(decoded_response['features'].values())
            appearances = int(model.predict([features]))

        else:
            appearances = int(dynamo_response['Items'][0]['appearances']['N'])


        body = {'link': link, 'appearances': appearances}

        return {
                'statusCode': 200,
                'body': json.dumps(body)
            }

    # If we dont find the model
    else:
        return {
                'statusCode': 500,
                'body': json.dumps('Model not found or not trained. Try again later.')
            }