import boto3
import json
import os

def lambda_handler(event, context):
    # Get the resources
    dynamodb = boto3.resource('dynamodb')
    
    # Setting the enviornment variable
    tableName = os.environ["Alarm_key"]
    table = dynamodb.Table(tableName)

    message = json.loads(event['Records'][0]['Sns']['Message'])
    
    table.put_item(
        Item={
            'MetricName': message["Trigger"]["MetricName"],
            'AlarmTime': event['Records'][0]['Sns']['AlarmTime'],
            'Region': message["Region"],
            'AlarmReason': message["NewStateReason"],
            'URL': message["Trigger"]["Dimensions"][0]["value"]
        },
    )
