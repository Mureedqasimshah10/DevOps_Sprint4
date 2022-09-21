from asyncio import constants
import resource
from urllib import request
import boto3
import json
import os
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key
import constants

# Getting the services resources
dynamodb = boto3.resource('dynamodb')
# Setting the enviroment variable
tableName = os.environ["URL_key"]
table = dynamodb.Table(tableName)


# # ----------------------------------------------------------------------------------------------------- # #
# # ----------------------------------------------------------------------------------------------------- # #
# #############  CRUD Operation (Create, Read, Update and Delete item in the DynamoDB table)   ##############
# # ----------------------------------------------------------------------------------------------------- # #
# # ----------------------------------------------------------------------------------------------------- # #
def lambda_handler(event, context):
    
    # Getting the method
    method = event['httpMethod']
    # Getting the method body
    body = event['body']
    load_id = json.loads(body)['LINKid']
    load_url = json.loads(body)['url']
    # Updating the value on the basis of partition key in DynamoDB Table
    # key = {'LINKid': body}
    # Reading the Item in the DynamoDB Table
    key ={
        "LINKid": str(load_id),
        "url": load_url
    }
    if method == 'GET':
        response = table.scan()['Items']
        if response:
            return json_response(response)
        else:
            return json_response({"message": "Nothing found"}, 404)
    
    # Deleting the Item in the DynamoDB Table
    elif method == 'DELETE':
        #  Loading the whole body and deleting the item by id_
        response = table.delete_item(
        Key=
        {
            "LINKid": str(load_id)
        })
        if response:
            return json_response({"message": "Given url is deleted successfully from the DynamoDB Table"})
        else:
            return json_response({"message": "Entered URL is not found"})
    
    # POST (Crating) the Item in the DynamoDB Table by Id
    elif method == 'POST':
        try:
            response = table.put_item(
                Item=key,
                ConditionExpression='attribute_not_exists(LINKid)'
            )
            if response:
                return json_response({"message": "Successfully added URL into the table"})

        except ClientError as e:
                if e.response['Error']['Code']=='ConditionalCheckFailedException':
                    return json_response({"message": "Your searched Link_ID already exits!"})
        
    # PUT (Updating) the Item in the DynamoDB Table by Id
    elif method == 'PUT':
        response = table.update_item(
            Key={
                'LINKid': str(load_id)
            },
            UpdateExpression='SET load_url = :u',
            ConditionExpression='attribute_not_exists(deletedAt)', 
            ExpressionAttributeValues={
                ':u': load_url
            },
            ReturnValues="UPDATED_NEW"
        )
        if response:
            return json_response({"message": "Successfully updated URL in the table"})
        else:
            return json_response({"message": "URL not found"})
    
    else:
        return json_response({"message": "Invalid Method. Please enter correct method\n POST: For adding GET: For reading DELETE: For removing UPDATE: For updating"})


def json_response(data):
    return {
        "statusCode": 200,
        "body": json.dumps(data),
        "headers": {'Content-Type': 'application/json'},
    }
