import boto3
# https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudwatch.html

class CloudwatchputMetric:
    def __init__(self):
        self.client = boto3.client("cloudwatch")        
    def put_data(self, nameSpace, metricName, dimension, value):
        response = self.client.put_metric_data(
            Namespace=nameSpace,
        MetricData=[
            {
                # Defining the first matric name, dimension and value
                'MetricName': metricName,
                'Dimensions': dimension,
                'Value': value,  
            },    
        ]
    )