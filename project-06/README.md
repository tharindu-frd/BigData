![Sample Image](image.jpg)

## Here we gonna build a transient EMR clsuter

### A transient EMR cluster is a temporary cluster that is created to perform a specific job or set of jobs, and then automatically terminates once the tasks are completed. It’s designed for short-term, on-demand processing, where you only pay for the resources while the cluster is running.

### In contrast, a persistent EMR cluster is designed to run continuously or for long periods. It remains active even after the jobs are completed, allowing for ongoing processing or the ability to submit new jobs without needing to set up a new cluster each time

### Our airlow layers :

- create_emr_cluster
- ingest_layer
- poll_step_layer (to check if the last layer is successfully completed )
- transform_layer
- poll_step_layer2 (to check if the last layer is successfully completed )
- terminate_emr_cluster
- snowflake_load

### Create EC2 , name: airflowcluster , go to that EC2 -> security groups -> edit inbound rules and allow all traffic from anywhere IPV4 . Now connect with that EC2 using mobaxterm .

```
sudo apt update
sudo apt install -y python3-pip
sudo apt install -y sqlite3
sudo apt-get install -y libpq-dev
pip3 install --upgrade awscli
pip3 install boto3
sudo pip3 install virtualenv
virtualenv venv
source venv/bin/activate
pip install "apache-airflow[postgres]==2.5.0" --constraint "https://raw.githubusercontent.com/apache/airflow/constraints-2.5.0/constraints-3.7.txt"
pip install pandas apache-airflow-providers-snowflake==2.1.0 snowflake-connector-python==2.5.1 snowflake-sqlalchemy==1.2.5
airflow db init
sudo apt-get install postgresql postgresql-contrib
sudo -i -u postgres
psql
CREATE DATABASE airflow;
CREATE USER airflow WITH PASSWORD 'airflow';
GRANT ALL PRIVILEGES ON DATABASE airflow TO airflow;
exit
exit
ls
cd airflow
sed -i 's#sqlite:////home/ubuntu/airflow/airflow.db#postgresql+psycopg2://airflow:airflow@localhost/airflow#g' airflow.cfg
sed -i 's#SequentialExecutor#LocalExecutor#g' airflow.cfg
airflow db init
airflow users create -u airflow -f airflow -l airflow -r Admin -e airflow1@gmail.com
User id --airflow
password--admin@123!
mkdir /home/ubuntu/dags
cd airflow
vi airflow.cfg

```

### change the below properties --

- dags_folder = /home/ubuntu/dags
- load_examples = False

### Now using winscp create a connection between our local machine and EC2 . Now in EC2 machine click on ubuntu in the path /home/ubuntu/airflow/ and click on dags and now drag our airflow_emr_spark_s3_snowflake.py and put it in their under dags .

### Now again run the following commands in mobaxterm

```

airflow db init
airflow webserver

source venv/bin/activate
airflow scheduler

```

### Now our airflow server is running . To get that copy the public IP of our EC2 , go the browser , <public-ip-of-Ec2>:8080 , username:admin , password:admin@123 . Now click on our dag -> click on Admin (top of the UI) -> connections -> click on that + icon

- connection Id : snowflake_conn
- connection Type : Snowflake
  ![Sample Image](image3.jpg)
- Host : wm60820.us-east-2.aws.snowflakecomputing.com
- Schema: PUBLIC
- Login:
- password:
- Account: wm60820.us-east-2.aws
- Warehouse: COMPUTE_WH
- Database: RAMU
  -Region: us-east-2.aws
  -Role: accountadmin

### wm60820 : account Id

### Now manually trigger the DAG

## Snowflake Queries:

![Sample Image](image4.jpg)
