from datetime import datetime
from urllib import response
import urllib3
import os
import boto3
from Cloudwatch_putMetrices import CloudwatchputMetric
import constants as constants

def lambda_handler(event, context):
    
    ## -------------------------------------------------------------------------##
    ## ---------- Here we are getting the list from the table-------------------##
    ## ---------- Append this list in the constant file ------------------------##
    ## -------------------------------------------------------------------------##
    dynamodb = boto3.resource('dynamodb')
    tableName = os.environ["URL_key"]
    table = dynamodb.Table(tableName)

    response = table.scan()['Items']
    for i in range(len(response)):
        constants.MY_VARIABLE.append(response[i]["url"])
        print(constants.MY_VARIABLE)




    for url in constants.MY_VARIABLE:
        values_ = dict()
        availability = getavailability(url)
        latency = getLatency(url)
        values_.update({"Availability ":availability,"Latency ":latency})
        print(values_)
        # I would like to publish my matrices to cloud watch
        cw = CloudwatchputMetric()
        dimension = [{'Name': 'URL', 'Value': url}]
        
        
        responseAvail = cw.put_data(constants.URL_MONITOR_NAMESPACE , 
        constants.URL_MONITOR_METRIC_NAME_AVAILABILITY,
        dimension,
        availability)
        
        responselatency = cw.put_data(constants.URL_MONITOR_NAMESPACE , 
        constants.URL_MONITOR_METRIC_NAME_LATENCY,
        dimension,
        latency)

    
    # Defining the funciton to obtain the availability
def getavailability(url):
    http = urllib3.PoolManager()
    # Sending the get request to access the webpage
    response = http.request("GET", url)
    if response.status ==200:
        return 1.0
    else:
        return 0.0

    
    # Defining the funciton to obtain the latency
def getLatency(url):
    # Calculating the how much time it takes for the user to access webpage
    http = urllib3.PoolManager()
    # starting our timer
    start = datetime.now()
    # Sending a request to access the webpage
    response = http.request("GET", url)
    # Ending the timer
    end = datetime.now()
    # returing the latency in seconds
    delta = end - start
    latencySec = round(delta.microseconds * .000001, 6)
    return latencySec