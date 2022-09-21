
# Build a public CRUD API Gateway endpoint for the web crawler to perform CRUD Operation on the target list containing the list of websites/webpages to crawl.

## Acknowledgements

I would like to thank Dr. Ayesha Binte Ashfaq for being helpful thorugout this week and for her precious time. In addition, I would like to thank SkipQ to give the golden opportunity to do this project.

## Overview

In this project we are building a public server-less CRUD API Gateway endpoint for the web crawler to create, read, update and delete the target URLs list in DynamoDB database table DynamoDB is a fully managed NoSQL database service that provides fast performance with seamless scalability.

### Learning outcomes

These are basics that we learned during this sprint4:

* Create and populate a URL table in DynamoDB.
* Implement CRUD REST commands on DynamoDB entries.
* Create Lambda handler to process API Gateway requests.
* Create public server-less REST API Gateway endpoint.
* Use CI/CD to automate multiple deployment stages (prod vs beta).
* Extend tests in each stage to cover the CRUD operations and DynamoDB read/write time.
* Manage README files and run-books in markdown on GitHub.

### What we achieve

The end goal of this sprint is to build a public serverless API Gateway endpoint using CRUD operations for the application so that clients can create, read, update, and delete items from a DynamoDB table.

## Environment Setup

* First install Windows Subsystem for Linux (WSL). For this, download WSL.exe file from Google. I faced error in installtion using wsl --install command so I used wsl.exe --install -d Ubuntu-20.04 commad to install it correctly.
* Dwnloaded VS Code and setup remote WSL from windows
* Download python3
* Donwload awscliv2.zip file from given path and install AWS. If you download it directly from google, there will be issue of path.
* Download and install NVM and NPM
* Check versions of all to be sure that softwares are installed corrrectly.

## Project Deployment - How to Run

* Open the ubuntu terminal and clone the git repository using git clone "forked-repo-github-url"
* Confirm that your working directory is Sprint4
* Activate the virtual environment using command source .venv/bin/activate
* Configure the aws using aws configure and add your email and username to global configuration using command
git config --global user.email "your-email.gmail.com" and git config --global user.name "your-name" 
* Edit commands in pipelines_.ShellStep to add path of your directory. cd RootFolderName/ProjectFolderName/
* Run pip install -r requirements.txt to install all required packages
* Push changes to github. git commit -m "commit message" and git push
* Synth and Deploy the project on Consile using cdk synth and cdk deploy.

## AWS Console Output
* Go to the AWS Console and monitore logs of WHLambda function for Availability and Latency.
* Go to the AWS Console and monitore logs of DBLambda function for records (if you print them).
* Go to the AWS DynamoDB database and check the item tables for records.
* Go to the AWS CodePipeline and check the deployment of all stages.

## TECHNOLOGIES USED

* AWS CI/CD CodePipeline
* AWS API Gateway
* AWS CodeBuild
* AWS CloudWatch
* AWS Github

## Refrences

* https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/Query.html#:~:text=and%20Indexes%3A%20.NET-,Key%20Condition%20Expressions%20for%20Query,-To%20specify%20the
* https://docs.aws.amazon.com/cdk/api/v1/python/aws_cdk.aws_sns_subscriptions/EmailSubscription.html
* https://docs.aws.amazon.com/lambda/index.html
* https://docs.aws.amazon.com/AmazonCloudWatch/latest/events/ScheduledEvents.html
* https://docs.aws.amazon.com/cdk/api/v1/python/aws_cdk.aws_dynamodb/TableProps.html
* https://docs.aws.amazon.com/cdk/api/v1/docs/@aws-cdk_core.RemovalPolicy.html

## Author
* Mureed Qasim Shah

## Useful commands

 * `cdk ls`          list all stacks in the app
 * `cdk synth`       emits the synthesized CloudFormation template
 * `cdk deploy`      deploy this stack to your default AWS account/region
 * `cdk diff`        compare deployed stack with current state
 * `cdk docs`        open CDK documentation

Enjoy!
