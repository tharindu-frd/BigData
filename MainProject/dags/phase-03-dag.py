import boto3
import logging
import airflow
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.contrib.operators.snowflake_operator import SnowflakeOperator
from airflow.contrib.hooks.snowflake_hook import SnowflakeHook
from airflow.operators.bash_operator import BashOperator
from datetime import datetime, timedelta
from time import sleep
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)



### In Amazon EMR (Elastic MapReduce), a JobFlow ID is a unique identifier for a cluster (formerly called a job flow) that is created when you start a new EMR cluster. This ID is used to manage and track the cluster and its associated tasks and steps throughout its lifecycle.



args = {"owner": "Airflow", "start_date": airflow.utils.dates.days_ago(2)}

dag = DAG(
    dag_id="snowflake_automation_dag", default_args=args, schedule_interval=None
)



client = boto3.client('emr', region_name='us-east-1',aws_access_key_id='{}',aws_secret_access_key='{}')

def create_emr_cluster():
  '''
  Starts a new EMR cluster with specified configurations (e.g., instance types, key pair, log URI). Returns the cluster ID of the created cluster.
  
  '''


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
    'Ec2KeyName': 'helloairflow',    # EC2 keypair 
    'KeepJobFlowAliveWhenNoSteps': True,
    'TerminationProtected': False,   ## So when the one task is completed cluster wont be terminated 
    'Ec2SubnetId': 'subnet-03a4055dd5d656279',
    },
    LogUri="s3://aws-glue-temporary-8256865577044-us-east-1/",   #"aws-glue-temporary-8256865577044-us-east-1"  : this is s3 bucket name where we store EMR logs 
    ReleaseLabel= 'emr-5.33.0',
    BootstrapActions=[],
    VisibleToAllUsers=True,
    JobFlowRole="EMR_EC2_DefaultRole",
    ServiceRole="EMR_DefaultRole",
    Applications = [ {'Name': 'Spark'},{'Name':'Hive'}])
  print("The cluster started with cluster id : {}".format(cluster_id))
  return cluster_id




  
def add_step_emr(cluster_id,jar_file,step_args):
  '''
   Adds a step to the EMR cluster to execute a specified JAR file with arguments. Returns the step ID of the added step.
  
  '''


  print("The cluster id : {}".format(cluster_id))
  print("The step to be added : {}".format(step_args))
  response = client.add_job_flow_steps(
  JobFlowId=cluster_id,
  Steps=[
  {
    'Name': 'test12',
    'ActionOnFailure':'CONTINUE',
    'HadoopJarStep': {
  'Jar': jar_file,
  'Args': step_args
  }
  },
  ]
  )
  print("The emr step is added")
  return response['StepIds'][0]
  

def get_status_of_step(cluster_id,step_id):
  '''
  Retrieves the current status of a given step in the EMR cluster using the step ID.
  '''

  response = client.describe_step(
    ClusterId=cluster_id,
    StepId=step_id
  )
  return response['Step']['Status']['State']
  
  

def wait_for_step_to_complete(cluster_id,step_id):
  '''
  Polls the status of an EMR step at regular intervals until the step completes. It waits for the step to finish before proceeding.

  '''

  print("The cluster id : {}".format(cluster_id))
  print("The emr step id : {}".format(step_id))
  while True:
    try:
      status=get_status_of_step(cluster_id,step_id)
      if status =='COMPLETED':
        break
      else:
        print("The step is {}".format(status))
        sleep(40)

    except Exception as e:
      logging.info(e)
	  

def terminate_cluster(cluster_id):
    '''
    Terminates the EMR cluster using the cluster ID. Handles exceptions if the termination fails.
    '''

    try:
        client.terminate_job_flows(JobFlowIds=[cluster_id])
        logger.info("Terminated cluster %s.", cluster_id)
    except ClientError:
        logger.exception("Couldn't terminate cluster %s.", cluster_id)
        raise
		
with dag:
  create_emr_cluster = PythonOperator(
  task_id='create_emr_cluster',
  python_callable=create_emr_cluster,
  dag=dag, 
  
  )
  transform_layer = PythonOperator(
  task_id='transform_layer',
  python_callable=add_step_emr,
  op_args=['command-runner.jar',[ 'spark-submit',
            '--master', 'yarn',
            '--deploy-mode', 'cluster',
            's3://data-archival/scripts/transform.py']],
  dag=dag, 
  )
  poll_step_layer2 = PythonOperator(
  task_id='poll_step_layer2',
  python_callable=wait_for_step_to_complete,
  op_args=['{{ ti.xcom_pull("create_emr_cluster")["JobFlowId"]}}','{{ ti.xcom_pull("transform_layer")}}'],
  dag=dag, 
  )
  terminate_emr_cluster = PythonOperator(
  task_id='terminate_emr_cluster',
  python_callable=terminate_cluster,
  op_args=['{{ ti.xcom_pull("create_emr_cluster")["JobFlowId"]}}'],
  dag=dag, 
  )
  snowflake_load=SnowflakeOperator(
		task_id="snowflake_load",
		sql="""ALTER EXTERNAL TABLE BIGDATA.PUBLIC.IBigdata2 REFRESH""" ,
		snowflake_conn_id="snowflake_conn"
	)

 

create_emr_cluster >> transform_layer >> poll_step_layer2 >> terminate_emr_cluster >> snowflake_load




'''
Final DAG Configuration

(01) create_emr_cluster Task:
       * Description: Executes the create_emr_cluster function to start a new EMR cluster. Task ID: create_emr_cluster.
         
         
(02) ingest_layer Task:
       * Description: Runs the add_step_emr function to add a step to the EMR cluster that uses script-runner.jar to execute a custom script (e.g., ingest.sh). Task ID: ingest_layer.


(03) poll_step_layer Task:       
       * Description: Uses the wait_for_step_to_complete function to check the status of the ingest step until it is completed. Task ID: poll_step_layer.
       
(04) transform_layer Task:
       * Description: Adds another step to the EMR cluster to run a Spark job using command-runner.jar to execute transform.py. Task ID: transform_layer.

(05) poll_step_layer2 Task:
       * Description: Uses the wait_for_step_to_complete function to check the status of the transform step until it is completed. Task ID: poll_step_layer2.


(06) terminate_emr_cluster Task:
       * Description: Executes the terminate_cluster function to stop and terminate the EMR cluster after all steps are finished. Task ID: terminate_emr_cluster.

(07) snowflake_load Task:
       * Description: Uses SnowflakeOperator to execute a SQL command that refreshes an external table in Snowflake. Task ID: snowflake_load.


Task Dependencies
       create_emr_cluster must complete before ingest_layer starts.
       ingest_layer must complete before poll_step_layer starts.
       poll_step_layer must complete before transform_layer starts.
       transform_layer must complete before poll_step_layer2 starts.
       poll_step_layer2 must complete before terminate_emr_cluster starts.
       terminate_emr_cluster must complete before snowflake_load starts.



'''