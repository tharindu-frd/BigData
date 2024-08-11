import json;
import boto3;

client = boto3.client('emr', region_name='us-west-2',aws_access_key_id='',aws_secret_access_key='')


def lambda_handler(event, context):
    file_name = event['Records'][0]['s3']['object']['key']
    bucketName=event['Records'][0]['s3']['bucket']['name']
    print("File Name : ",file_name)
    print("Bucket Name : ",bucketName)
    backend_code="s3://codefilelocation/spark.py"
    spark_submit = [
    'spark-submit',
    '--master', 'yarn',
    '--deploy-mode', 'cluster',
    backend_code,
    bucketName,
    file_name
    ]
    print("Spark Submit : ",spark_submit)
    cluster_id = client.run_job_flow(
    Name="transient_demo_testing",
    Instances={
    'InstanceGroups': [
    {
    'Name': "Master",
    'Market': 'ON_DEMAND',
    'InstanceRole': 'MASTER',
    'InstanceType': 'm1.xlarge',
    'InstanceCount': 1,
    },
    {
    'Name': "Slave",
    'Market': 'ON_DEMAND',
    'InstanceRole': 'CORE',
    'InstanceType': 'm1.xlarge',
    'InstanceCount': 2,
    }
    ],
    'Ec2KeyName': '{key_name',     ### We need to  create a keyname pair , so it will attach to the EC2 where our EMR clsuter gonna be launched 
    'KeepJobFlowAliveWhenNoSteps': False,
    'TerminationProtected': False,
    'Ec2SubnetId': 'subnet-726ad13b',   ### Here we have given a defaut subnet 
     },
    LogUri="s3://aws-logs-137360334857-us-west-2/elasticmapreduce",
    ReleaseLabel= 'emr-5.33.0' , # '{Specify emr version}
    Steps=[{"Name": "testJobGURU",
    'ActionOnFailure': 'CONTINUE',
    'HadoopJarStep': {
    'Jar': 'command-runner.jar',
    'Args': spark_submit
    }
    }],
    BootstrapActions=[],
    VisibleToAllUsers=True,
    JobFlowRole="EMR_EC2_DefaultRole",
    ServiceRole="EMR_DefaultRole",
    Applications = [ {'Name': 'Spark'},{'Name':'Hive'}])

    





############### Code Breakdown     ####################
## LogUri - The path to the Amazon S3 location where logs for this cluster are stored.

## Applications - The applications installed on this cluster.Hive, and Spark have been chosen here. There are other applications available such as Hadoop,Pig, Oozie, Zookeeper, etc.
# Example : If you require Hadoop , Hive, Spark  then you can specify the configuration like this --
# Applications = [
#            {'Name' : 'Hadoop'},
#           {'Name' : 'Hive'},
#            {'Name' : 'Spark'}
#       ]



## Instances - Describes the Amazon EC2 instances of the job flow.
## InstanceGroups - This represents an instance group, which is a group of instances that have a common purpose. For example, the CORE instance group is used for HDFS.
## Market - The marketplace to provision instances for this group. Valid values are ON_DEMAND or SPOT. 
## TerminationProtected - Indicates whether Amazon EMR will lock the cluster to prevent the EC2 instances from being terminated by an API call or user intervention, or in the event of a cluster error.

## JobFlowRole - Also called instance profile and EC2 role. An IAM role for an EMR cluster. The EC2 instances of the cluster assume this role. The default role is EMR_EC2_DefaultRole.
## ServiceRole - The IAM role that will be assumed by the Amazon EMR service to access AWS resources on your behalf.
## VisibleToAllUsers-Indicates whether the cluster is visible to IAM principals in the Amazon Web Services account associated with the cluster. 
## ReleaseLabel  -- The Amazon EMR release label, which determines the version of open-source application packages installed on the cluster.    
## Ec2KeyName -- The name of the EC2 key pair that can be used to connect to the master node using SSH as the user called "hadoop."
## KeepJobFlowAliveWhenNoSteps -- Specifies whether the cluster should remain available after completing all steps. Defaults to true .
