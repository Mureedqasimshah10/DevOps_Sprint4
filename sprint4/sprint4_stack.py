from random import random
from aws_cdk import (
    Duration,
    Stack,
    aws_lambda as lambda_,
    RemovalPolicy,
    aws_events as events_,
    aws_events_targets as targets_,
    aws_cloudwatch as cloudwatch_,
    aws_iam as iam_,
    aws_sns as sns_,
    aws_cloudwatch_actions as cw_actions_,
    aws_sns_subscriptions as subscriptions_,
    aws_dynamodb as dynamodb_,
    aws_codedeploy as codedeploy_,
    aws_apigateway as apigateway_,
    )
from constructs import Construct
from resources import constants as constants
import random
class Sprint4Stack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Creating my lambda function for deploying hw_lambda.py function 
        # Creating another lambda funciton for structuring the data to put into Dynamo Database
        # https://docs.aws.amazon.com/cdk/api/v1/python/aws_cdk.aws_lambda/Function.html
        # Assigning the role to the created lambda function
        
        lambda_role = self.create_lambda_role()
        hw_lambda = self.create_lambda("MyFirstLambda", "hw_lambda.lambda_handler", "./resources", lambda_role)      
        db_lambda = self.create_lambda("QasimDynamoDBLambda", "DynamoDBLambda.lambda_handler", "./resources", lambda_role)
        
        # Create a dynamo db table in stack
        # Creating the enviornment variable and passing the parameters
        DBTable = self.create_table()
        tname = DBTable.table_name
        db_lambda.add_environment(key="Alarm_key", value=tname)
        

        # Defining an event 
        # https://docs.aws.amazon.com/cdk/api/v1/python/aws_cdk.aws_events/Schedule.html
        # Generating event every one minute
        schedule = events_.Schedule.rate(Duration.minutes(60))
        # Defining the target for our lambda function and the event
        target = targets_.LambdaFunction(handler=hw_lambda)
        rule = events_.Rule(self, "LambdaEventRule",
        description="This is my rule for generation of auto event for my hw_lambda function",
        schedule=schedule,
        targets=[target]
        )

        # Creating my SNS topic (i.e. message server to connect with alarm for notification)
        # https://docs.aws.amazon.com/cdk/api/v1/python/aws_cdk.aws_sns/Topic.html
        topic = sns_.Topic(self, "Alarmnotification")
        # https://docs.aws.amazon.com/cdk/api/v1/python/aws_cdk.aws_sns_subscriptions/EmailSubscription.html
        email_address = "qasim.shah.skipq@gmail.com"
        topic.add_subscription(subscriptions_.EmailSubscription(email_address))
        topic.add_subscription(subscriptions_.LambdaSubscription(db_lambda))
         
        # # ----------------------------------------------------------------------------------------------------- # #
        # # ----------------------------------------------------------------------------------------------------- # #
        # #######################################  Sprint3: Stack Code    ########################################### 
        # # ----------------------------------------------------------------------------------------------------- # #
        # # ----------------------------------------------------------------------------------------------------- # #

        # Generating alarms on Duration adn Invocation during deployment
        # https://docs.aws.amazon.com/cdk/api/v1/python/aws_cdk.aws_lambda/Function.html
        hw_lambdaMetric = hw_lambda.metric('Duration', period=Duration.minutes(60))
        # https://docs.aws.amazon.com/cdk/api/v1/python/aws_cdk.aws_cloudwatch/Alarm.html
        DurationAlarm = cloudwatch_.Alarm(self, "hw_lambdaDurationAlarm",
                comparison_operator=cloudwatch_.ComparisonOperator.GREATER_THAN_THRESHOLD,
                threshold=100,
                evaluation_periods=1,
                metric=hw_lambdaMetric
            )
        
        # https://docs.aws.amazon.com/cdk/api/v1/python/aws_cdk.aws_lambda/Function.html    
        hw_lambdaInvoMetric = hw_lambda.metric('Invocations', period=Duration.minutes(60))
        # https://docs.aws.amazon.com/cdk/api/v1/python/aws_cdk.aws_cloudwatch/Alarm.html
        InvocationAlarm = cloudwatch_.Alarm(self, "hw_lambdaInvoAlarm",
                comparison_operator=cloudwatch_.ComparisonOperator.GREATER_THAN_THRESHOLD,
                threshold=100,
                evaluation_periods=1,
                metric=hw_lambdaInvoMetric
            )

        #Adding alarms action. 
        DurationAlarm.add_alarm_action(cw_actions_.SnsAction(topic))    
        InvocationAlarm.add_alarm_action(cw_actions_.SnsAction(topic))

        random_nbr = random.randint(0,999)

        # Lambda deployment configuration and rollback
        # https://docs.aws.amazon.com/cdk/api/v1/python/aws_cdk.aws_lambda/Alias.html#aws_cdk.aws_lambda.Alias
        version = hw_lambda.current_version
        alias = lambda_.Alias(self, "Qasim_Lambda_Alias" + str(random_nbr),
            alias_name="Prod_MureedAlias" + str(random_nbr),
            version=version
            )
        
        # https://docs.aws.amazon.com/cdk/api/v1/python/aws_cdk.aws_codedeploy/LambdaDeploymentGroup.html
        deployment_group = codedeploy_.LambdaDeploymentGroup(self, "QasimLambdaDeployment",
            alias = alias,
            alarms = [DurationAlarm, InvocationAlarm],   
            deployment_config = codedeploy_.LambdaDeploymentConfig.LINEAR_10_PERCENT_EVERY_1_MINUTE
        )


        # # ----------------------------------------------------------------------------------------------------- # #
        # # ----------------------------------------------------------------------------------------------------- # #
        # #######################################  Sprint3 Code Ended  ############################################## 
        # # ----------------------------------------------------------------------------------------------------- # #
        # # ----------------------------------------------------------------------------------------------------- # #
        # ##################################  Sprint4: Code Creating an API Gateway  ################################
        # # ----------------------------------------------------------------------------------------------------- # #
        # # ----------------------------------------------------------------------------------------------------- # #
        # Create lambda function for integration with API Gateway 
        api_lambda = self.create_lambda("QasimAPILambda", "APILambdaOverHTTP.lambda_handler", "./resources", lambda_role)
        # Add table to environment variables of lambda functions
        APITable = self.API_create_table()
        apitable = APITable.table_name
        api_lambda.add_environment(key="URL_key", value=apitable)
        hw_lambda.add_environment(key="URL_key", value=apitable)

        # Define an API Gateway REST API with AWS Lambda proxy integration
        # https://docs.aws.amazon.com/cdk/api/v1/python/aws_cdk.aws_apigateway/README.html
        # https://docs.aws.amazon.com/cdk/api/v1/python/aws_cdk.aws_apigateway/README.html#endpoint-configuration
        api = apigateway_.LambdaRestApi(self, id = "mureed_api",
            handler=api_lambda,
            proxy=False,
            endpoint_configuration=apigateway_.EndpointConfiguration(
            types=[apigateway_.EndpointType.REGIONAL]
            ))

        # Giving the API GATEWAY Permission to invoke my api_lambda function
        # https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_lambda/Function.html#aws_cdk.aws_lambda.Function.grant_invoke
        api_lambda.grant_invoke(iam_.ServicePrincipal("apigateway.amazonaws.com"))


        # Define the API CRUD model using addMethod function
        # https://docs.aws.amazon.com/cdk/api/v1/python/aws_cdk.aws_apigateway/Resource.html
        # https://docs.aws.amazon.com/cdk/api/v1/python/aws_cdk.aws_apigateway/IResource.html#aws_cdk.aws_apigateway.IResource.add_method
        items = api.root.add_resource("items")
        items.add_method("GET")            # GET Read /items
        items.add_method("POST")           # POST Create /items
        items.add_method("DELETE")         # DELETE: /items
        items.add_method("PUT")            # PUT: (Update) /items

        # # ----------------------------------------------------------------------------------------------------- # #
        # # ----------------------------------------------------------------------------------------------------- # #
        # #######################################  Sprint4 Code Ended  ############################################## 
        # # ----------------------------------------------------------------------------------------------------- # #
        # # ----------------------------------------------------------------------------------------------------- # #
        

       
        for url in constants.MY_VARIABLE:
            # Creating Availability and Latenct matrices
            dimensions={"URL": url}
            # https://docs.aws.amazon.com/cdk/api/v1/python/aws_cdk.aws_cloudwatch/Metric.html
            availMetric = cloudwatch_.Metric(metric_name=constants.URL_MONITOR_METRIC_NAME_AVAILABILITY, 
            namespace=constants.URL_MONITOR_NAMESPACE,  
            dimensions_map=dimensions,
            period=Duration.minutes(60) 
            )

            # https://docs.aws.amazon.com/cdk/api/v1/python/aws_cdk.aws_cloudwatch/Metric.html
            latencyMetric = cloudwatch_.Metric(metric_name=constants.URL_MONITOR_METRIC_NAME_LATENCY, 
            namespace=constants.URL_MONITOR_NAMESPACE,  
            dimensions_map=dimensions,
            period=Duration.minutes(60) 
            )

            # Generating alarms on availability and latency matrices
            # https://docs.aws.amazon.com/cdk/api/v1/python/aws_cdk.aws_cloudwatch/Alarm.html
            availAlarm = cloudwatch_.Alarm(self, "AvailabilityAlarm"+url,
                comparison_operator=cloudwatch_.ComparisonOperator.LESS_THAN_THRESHOLD,
                threshold=1,
                evaluation_periods=1,
                metric=availMetric
            )

            # https://docs.aws.amazon.com/cdk/api/v1/python/aws_cdk.aws_cloudwatch/Alarm.html
            latencyAlarm = cloudwatch_.Alarm(self, "LatencyAlarm"+url,
                comparison_operator=cloudwatch_.ComparisonOperator.GREATER_THAN_THRESHOLD,
                threshold=0.4,
                evaluation_periods=1,
                metric=latencyMetric
            )

            #  https://docs.aws.amazon.com/cdk/api/v1/python/aws_cdk.aws_cloudwatch_actions/SnsAction.html
            # Configuring alarm with notification services
            availAlarm.add_alarm_action(cw_actions_.SnsAction(topic))
            latencyAlarm.add_alarm_action(cw_actions_.SnsAction(topic))
            
            # Removal Policy to destory services
            hw_lambda.apply_removal_policy(RemovalPolicy.DESTROY)
            db_lambda.apply_removal_policy(RemovalPolicy.DESTROY)
            availAlarm.apply_removal_policy(RemovalPolicy.DESTROY)
            latencyAlarm.apply_removal_policy(RemovalPolicy.DESTROY)
            # DurationAlarm.apply_removal_policy(RemovalPolicy.DESTROY)
            # InvocationAlarm.apply_removal_policy(RemovalPolicy.DESTROY)
            topic.apply_removal_policy(RemovalPolicy.DESTROY)
            api.apply_removal_policy(RemovalPolicy.DESTROY)
            
 
        # https://docs.aws.amazon.com/cdk/api/v1/python/aws_cdk.aws_lambda/Function.html
    def create_lambda(self, id_, handler, path, my_role):
        return lambda_.Function(self, id_,
        runtime=lambda_.Runtime.PYTHON_3_8,
        handler=handler,
        code=lambda_.Code.from_asset(path), 
        role= my_role,
        timeout=Duration.seconds(600)
    )

    # https://docs.aws.amazon.com/cdk/api/v1/python/aws_cdk.aws_dynamodb/Table.html
    def create_lambda_role(self):
        lambda_role = iam_.Role(self, "lambda_role",
        assumed_by=iam_.ServicePrincipal("lambda.amazonaws.com"),
        managed_policies=[ 
                            iam_.ManagedPolicy.from_aws_managed_policy_name('CloudWatchFullAccess'),
                            iam_.ManagedPolicy.from_aws_managed_policy_name('AmazonDynamoDBFullAccess')
                        ])
        return lambda_role  

    # Creating table  
    def create_table(self):
        return dynamodb_.Table(self, "AlarmInfoTable",
        removal_policy=RemovalPolicy.DESTROY,
        # https://docs.aws.amazon.com/cdk/api/v1/python/aws_cdk.aws_dynamodb/Attribute.html#aws_cdk.aws_dynamodb.Attribute
        partition_key = dynamodb_.Attribute(name="MetricName", type=dynamodb_.AttributeType.STRING),
        sort_key = dynamodb_.Attribute(name="AlarmTime", type=dynamodb_.AttributeType.STRING),
    )
    
    # Creating another table   
    def API_create_table(self):
        return dynamodb_.Table(self, "QasimAPILambdaInfoTable",
        removal_policy=RemovalPolicy.DESTROY,
        # https://docs.aws.amazon.com/cdk/api/v1/python/aws_cdk.aws_dynamodb/Attribute.html#aws_cdk.aws_dynamodb.Attribute
        partition_key = dynamodb_.Attribute(name="LINKid", type=dynamodb_.AttributeType.STRING),
    )
    