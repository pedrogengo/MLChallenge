import boto3
import logging
import json
import os

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

class Link():
    def __init__(self, url):
        self.url = url
    
    @property
    def feature1(self):
        return len(self.url)
    
    @property
    def feature2(self):
        count = 0
        for i in self.url:
            if i == '/':
                count += 1
        return count
    
    @property
    def feature3(self):
        count = 0
        for i in self.url:
            if i in ['a', 'e', 'i', 'o', 'u']:
                count += 1
        return count
    
    @property
    def feature4(self):
        flag = 0
        if '.edu' in self.url:
            flag = 1
        return flag
    
    @property
    def feature5(self):
        flag = 0
        if '.br' in self.url:
            flag = 1
        return flag

    @property
    def feature6(self):
        count = 0
        for i in self.url:
            if i.isalpha():
                count += 1
        return count
    
    @property
    def feature7(self):
        count = 0
        for i in self.url:
            if i.isdigit():
                count += 1
        return count
    
    @property
    def feature8(self):
        end = self.url.split('.')[-1]
        return len(end)
    
    @property
    def feature9(self):
        cut_url = self.url.split('.')
        len_cut_url = [len(i) for i in cut_url]
        return max(len_cut_url)
    
    @property
    def feature10(self):
        return 3
    
    def get_features(self):
        features = {
            'feature1': self.feature1,
            'feature2': self.feature2,
            'feature3': self.feature3,
            'feature4': self.feature4,
            'feature5': self.feature5,
            'feature6': self.feature6,
            'feature7': self.feature7,
            'feature8': self.feature8,
            'feature9': self.feature9,
            'feature10': self.feature10,
        }
        return features

def update_features(client, table, link, features):

    response = client.update_item(
        TableName=table,
        Key={
            'link': {
                'S': link,
            }
        },
        UpdateExpression="set features=:f",
        ExpressionAttributeValues={
            ':f': {"M": features}
        },
        ReturnValues="UPDATED_NEW"
    )
    return response


def handler(event, context):

    # Starting dynamodb client
    client = boto3.client('dynamodb')

    # Getting link from event arg
    link = event['link']
    tablename = os.environ['TABLE_NAME']
    
    # Query to verify if the link exists in our table
    response = client.query(
        ExpressionAttributeValues={
            ':v1': {
                'S': link,
            },
        },
        KeyConditionExpression='link = :v1',
        TableName=tablename,
    )

    # If link not found, create the features and insert in table
    if len(response['Items']) == 0:
        link_instance = Link(link)
        features = link_instance.get_features()
        dynamo_features = {feature: {'N': str(value)} for feature, value in features.items()}
        response = client.put_item(
            TableName=tablename,
            Item={
                'link': {
                    'S': link,
                },
                'features': {
                    'M': dynamo_features
                },
                'appearances': {
                    'N': '0'
                }
            }
        )

    elif len(response['Items']) == 1:
        if response['Items'][0].get('features'):
            features = dict()
            for feature, v in response['Items'][0]['features']['M'].items():
                features[feature] = list(v.values())[0]
        
        # Link was found but it dont have features yet. So, we need to create then
        else:
            link_instance = Link(link)
            features = link_instance.get_features()
            dynamo_features = {feature: {'N': str(value)} for feature, value in features.items()}
            response = update_features(client, tablename, link, dynamo_features)
    else:
        raise Exception("Error when calling DynamoDB. Try again later")
    
    body = {
            'link': link,
            'features': features
        }

    return {
        'statusCode': 200,
        'body': json.dumps(body)
    }