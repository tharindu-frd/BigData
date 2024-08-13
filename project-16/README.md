# Serverless DataLake using an AWS Glue , Lambda , Cloudwatch

!(sample image)[image.jpg]

## step 01 : First create a s3 bucket called serverlessdemoglyelambdacloudwatch . Inside that bucket creaete 2 folders

- csvdatastorerforse
- parquetdatastorerforse

## step 02 : aws lambda -> createa a function

- Runtime: Python 3.9

#### Lambda Code to trigger Glue Crawler:

```python

import json
import boto3
glue=boto3.client('glue');

def lambda_handler(event, context):
       # TODO implement
       response = glue.start_crawler(
       Name='demoserveriestriggerbasedtechnique'   # this is name of the crawler that we gonna create later on
       )
       return {
              'statusCode': 200,
              'body': json.dumps('Hello from Lambda!')
}

```

#### Now go to configutaion section of the lambda we created -> Security Role -> Add permissions -> Attach policies ->

#### Now go to configutaion section -> Edit -> edit the timeout time

- Amazons3FullAccess
- AWSGlueServiceRole

#### Now click on addd trigger in our Lambda function

- storage : s3
- event type : all object create events
- prefix : csvdatastorerforse/

## step 03 : AWS Glue -> Crawler -> add crawler ->

- name : demoserveriestriggerbasedtechnique
- data store : s3
  -Include path : s3://serverlessdemoglyelambdacloudwatch/csvdatastorerforse/
- Create an IAM role : use case is Glue | Amazons3FullAccess | AWSGlueServiceRole | CloudWatchFulAcess
- add a db too (name:demotesting)

## step 04: aws lambda -> create a function -> - Runtime: Python 3.9

```python
import json
import boto3

def lambda_handler(event, context):
       glue=boto3.client('glue');
       response = glue.start_job_run(JobName = "demoserverless")
       print("Lambda Invoke")
```

#### Now go to configutaion section of the lambda we created -> Security Role -> Add permissions -> Attach policies ->

#### Now go to configutaion section -> Edit -> edit the timeout time

- Amazons3FullAccess
- AWSGlueServiceRole

## step 05: Aws Glue -> jobs -> Add jobs ->

- name :demoserverless
- This jobs runs : A new script to be authored by you , click on next -> save jobs and edit script

```python
import sys
from awsglue.transforms import \*
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job

@params: [JOB_NAME]
args = getResolvedOptions(sys.argv, ['JOB_NAME'])

sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

datasource0 = glueContext.create_dynamic_frame.from_catalog(database = "demotesting", table_name = "csvdatastorerforse", transformation_ctx = "datasource0")
## table name always gonna be the folder name unless we change it

datasink4 = glueContext.write_dynamic_frame.from_options(frame = datasource0, connection_type = "s3",
connection_options = {"path": "s3://serverlessdemoglyelambdacloudwatch/parquetdatastorerforse/"}, format = "parquet", transformation_ctx = "datasink4")
job.commit()

```

## step 06: Cloudwatch rule for trigger the Lambda on success of the Glue Crawler:

- Service Name : Glue
- Event type : Glue Crawler State Change
- click on specific staets : Succeeded
- click on add target and select the the lmabda which triggers the glue job

```
{
"source": [
"aws.glue"
],
"detail-type": [
"Glue Crawler State Change"
],
"detail": {
"state": [
"Succeeded"
],
"crawlerName": [
"demoserveriestriggerbasedtechnique"
]
}
}
```

#### Goto aws console -> SNS -> createa a one

## step 06: Cloudwatch rule for final notification part

- Service Name : Glue
- Event type : Glue jobs state changes
- click on specific staets : Succeeded
- click on add target and select the the SNS name we created

```
{
  "source": [
    "aws.glue"
  ],
  "detail-type": [
    "Glue Job State Change"
  ],
  "detail": {
    "jobName": [
      "demoserverless"
    ],
    "state": [
      "SUCCEEDED"
    ]
  }

}
```
