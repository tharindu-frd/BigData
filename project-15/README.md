# ETL | AWS Glue | AWS S3 | Load Data from AWS S3 to Amazon RedShift

!(sample image)[image.jpg]

## step 01 : Goto aws -> Redshift -> create a redshift cluster -> now click on the cluster we created -> go to editor and run the following query to create a table

```sql

create table cqpocsredshiftdemo (
  industry_name_ANZSIC varchar(100)    not null,
  rme_size_grp     	   varchar(100)    not null,
  variables        	   varchar(100)    not null
)
```

## step 02: create a s3 bucket and put the csv file inside that . Also create an IAM role with adminaccess

## step 02 : AWS console -> Glue -> Connections -> create a connection

- connection type: Redshift
- select the redshift cluster we created

### AWS console -> Cloudwatch -> Rules -> create a rule with the following pattern

```

{
"detail-type": [
"Glue Crawler State Change"
],
"source": [
"aws.glue"
],
"detail": {
"crawlerName": [
"DataSourceS3"
],
"state": [
"Succeeded"
]
}
}

```

### AWS console -> lambda ->create a function -> create a function

```python

# Set up logging
import json
import os
import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Import Boto 3 for AWS Glue
import boto3
client = boto3.client('glue')

# Variables for the job:
glueJobName = "TestJobDemo"

# Define Lambda function
def lambda_handler(event, context):
    logger.info('## TRIGGERED BY EVENT: ')
    logger.info(event['detail'])
    response = client.start_job_run(JobName = glueJobName)
    logger.info('## STARTED GLUE JOB: ' + glueJobName)
    logger.info('## GLUE JOB RUN ID: ' + response['JobRunId'])
    return response

```

### For that lambda set the the cloudwatch we created as the trigger

### AWS console -> Glue -> Crawler -> add a crawler ->

- name : DataSourceS3
- data store : s3
- assign the IAM role we created
- Frequency : run on demand
- create a db as well

### AWS console -> Glue -> Crawler -> add a crawler ->

- name : RedshiftDB
- data store : JDBC
- connection : select the connection we created
- Include path : select the path of our csv file
- assign the IAM role we created
- Frequency : run on demand
- create a db as well

### Aws Glue -> Jobs -> Add job

- name : TestjobDemo
- data source : s3bucket
- target : redshift cluster we created
