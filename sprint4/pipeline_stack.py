from math import gamma
import unittest
from aws_cdk import (
    Duration,
    Stack,
    pipelines as pipeline_,
    aws_codepipeline_actions as actions_
    )
import aws_cdk as cdk
from constructs import Construct
from sprint4.pipeline_stage import MyStage
class MyPipelineStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        # https://docs.aws.amazon.com/cdk/api/v1/python/aws_cdk.pipelines.html

        source = pipeline_.CodePipelineSource.git_hub("mureedqasim2022skipq/Pegasus_Python", "main",
        # https://docs.aws.amazon.com/cdk/api/v1/python/aws_cdk.core/SecretValue.html#aws_cdk.core.SecretValue
        authentication = cdk.SecretValue.secrets_manager('qasimtokenNew'),
        trigger=actions_.GitHubTrigger('POLL') 
        )
        
        # Output build Artifact
        # https://docs.aws.amazon.com/cdk/api/v1/python/aws_cdk.pipelines.html
        synth = pipeline_.ShellStep("synth", 
            input=source,
            commands=['cd mureed/sprint4/', 
            'pip install -r requirements.txt', 
            'npm install -g aws-cdk', 
            'cdk synth'],
            primary_output_directory="mureed/sprint4/cdk.out"
        )
        # https://docs.aws.amazon.com/cdk/api/v1/python/aws_cdk.pipelines/README.html
        mypipeline = pipeline_.CodePipeline(self, "MureedPipeline",
            synth=synth
        )
    
        unit_test = pipeline_.ShellStep("Unit Testing", 
            commands=['cd mureed/sprint4/', 
            'pip install -r requirements.txt', 
            'pip install -r requirements-dev.txt', 
            'pytest']
        )

        # Defining stages.
        beta = MyStage(self, "QasimBetaStage")
        prod = MyStage(self, "QasimProdStage")
        
        # Adding stages into our pipeline
        # https://docs.aws.amazon.com/cdk/api/v1/python/aws_cdk.core/Stage.html
        mypipeline.add_stage(stage=beta, pre=[unit_test])
        # https://docs.aws.amazon.com/cdk/api/v1/python/aws_cdk.pipelines/Step.html#aws_cdk.pipelines.Step 
        mypipeline.add_stage(stage=prod, pre=[pipeline_.ManualApprovalStep("PromoteToProd")])