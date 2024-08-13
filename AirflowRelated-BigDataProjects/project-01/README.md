# Automate a python ETL pipeline with airflow on AWS EC2

!(sample image)[image.jpg]

## step 01 : Create an EC2 instance . Create a new key pair and download the pem file . Edit the inbound rules and allow alltrafic from anywhere IPV4 . After that connect with that using MobaXterm .

```
sudo apt update
sudo apt install python3-pip
sudo apt install python3.10-venv
python3 -m venv airflow_venv
sudo pip install pandas
sudo pip install s3fs
sudo pip install apache-airflow
airflow standalone    # this will give the username and password

```

#### To get the airflow UI , <public-ip-of-EC2>:8080

#### Now lets connect to that EC2 using vs code . Open up the vscode and in the left botom corner there is a blue color icon click on that and select Connect to Host -> Configure ssh host -> select C:\Users\Tharindu\.ssh\config . Inside that

```
Host <EC2-instance-name>
       Hostname <public-ip-of-EC2>
       user Ubuntu
       IdentityFile C:/Users/Tharindu/.ssh/<pem-file-name>.pem

```

#### Now click on that blue icon -> Connect to host and select the EC2 instance that we want to connect to

#### Now under the folder airflow create a new folder called dags Inside that create a file called weatherapi_dag.py

#### Now go to airflow UI -> Admin -> create connection

- Connection Id : weathermap_api
- connection Type: HTTP
- Host : https://api.openweathermap.org

#### Now create a s3 bucket

#### Now createa an IAM role with AmazonEC2FullAccess | Amazons3FullAccess

#### Now create a folder called .aws and under that create a file called config and another file called credentials

- credentials

```
aws_access_key_id =
aws_secret_access_key=
```

- config

```
region  = us-west-2
```

#### Now open up a terminal

```
source airflow-venv/bin/activate
sudo apt install awscli
aws configure
aws sts get-session-token
```

#### Now put those credentials under aws_credentials in our weatherapi_dag.py file
