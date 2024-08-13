# End to End Streaming Data Pipeline Using AWS MSK & AWS Serverless Services

!(sample image)[image.jpg]

### Step 1:

-Cretae VPC -- Name -- virtual-private-cloud-lambda IPv4 CIDR -- 11.0.0.0/16

- Host address range -- 11.0.0.1 - 11.0.255.254

### Step 2:

- Create 2 public subnets
- Public-Subnet-A-lambda--11.0.0.0/24--us-east-1a
- Host address range -- 11.0.0.1 - 11.0.0.254

- Public-Subnet-B-lambda--11.0.1.0/24--us-east-1b
- Host address range -- 11.0.1.1 - 11.0.1.254

- Private-Subnet-A-lambda--11.0.2.0/24--us-east-1a
- Host address range -- 11.0.2.1 - 11.0.2.254

- Private-Subnet-B-lambda--11.0.3.0/24--us-east-1b
- Host address range -- 11.0.3.1 - 11.0.3.254

## Step 3 (Create an IGW and attach with VPC)

- Go to Internet Gateway -> Create internet gateway - > Once we crated it , click on that , then click on Attach to a vpc , and then select the VPC that we have created

## Step 4:

- Create 2 route tables 1 for Public subnets and 1 for Private subnets
- (Attach IGW with Public route tables)
- Go to Route Tables -> create route table
- Name : public route table
- VPC : select the VPC that we have created
- After that click on Edit routes -> Add routes
- Destination : 0.0.0.0/0
- Target : igw - ( Here select the internet gateway we have created )
- Now click on subnet associations

!(sample image)[project-12/image3.jpg]

### Now click on subnet associations -> Edit subnet associations

!(sample image)[project-12/image4.jpg]

- Go to Route Tables -> create route table
- Name : private route table
- VPC : select the VPC that we have created
- After that click on Edit routes -> Add routes
- Destination : 0.0.0.0/0
- Target : igw - ( Here select the internet gateway we have created )

  Now click on subnet associations -> Edit associations

  !(sample image)[project-12/image5.jpg]

  ## Step 5 : (Create NAT Gateway in public subnet and attach with Private Subnet route table )

- Now go to NAT Gateway -> create NAT Gateway
- Name : demoytlambdatrigger
- Subnet : selct public subnet A lambda
- connectivity type : public
- click on alocate elastic Ip
- Now go back to route tables -> click on private route tables -> Edit routes -> Add route ->
- Destinations : 0.0.0.0/0
- Target : select the NAT gateway we have created

## Step 6:

- Launch MSK Cluster in Private subnets
- cluster-type : Provisioned
- kafka version : 2.8.1
- broker type : t3.small
- number of zones : 2
- brokers per zone : 1
- Amazon EBS Storage per broker : 1GiB
- Select VPC we have created
- select the both private subnets and their zones
- public access : off
- keep unauthorised access and plaintext authentication

## Step 7 Create a Lambda code : This is the producer lambda code . It is responsible to read the data from SQS and publish it to the MSK cluster(Python 3.8)

- No go to aws lambda -> create a function ->
- Function name : producerlambdamskproject
- Runtime : python 3.8
- then create it . After that go to code and paste the following code there and after that click on deploy

```python
from time import sleep
from json import dumps
from kafka import KafkaProducer
import json

topic_name='{Provide the topic name here}'
producer = KafkaProducer(bootstrap_servers=['Put the broker URLs here'
,'Put the broker URLs here'],value_serializer=lambda x: dumps(x).encode('utf-8'))

def lambda_handler(event, context):
print(event)
for i in event['Records']:
sqs_message =json.loads((i['body']))
print(sqs_message)
producer.send(topic_name, value=sqs_message)

    producer.flush()
```

- Increase the timeout for Lambda to 2 mins , provide SQS,MSK and VPC access & put in Private VPC (where MSK Brokers are running) .
- To do this fist go to lambda function we crated -> configurations -> Edit -> Now increase the time out
- Go to lambda function we crated -> configurations -> Permissions -> Click on Role name -> Permissions and attach the following policies
- AmazonVPCFUllAccess
- AWSLambdaMSKExecutionRole
- AmazonSQSFullAccess
- Go to lambda function we crated -> configurations -> VPC -> Select the VPC that our MSK cluster is running -> after that select 2 private subnets and their zones as our brokers are running on those private subnets . And also select the security group of our MSK.

### Now go to configurations -> Edit -> Edit the time out so we wont be having any time out issues

### Now go to configurations -> permissions- > click on Role name -> permissions -> add permission -> Attach following policies

- AWSLambdaMSKExecutionRole
- AmazonVPCFullAccess

### Now go to aws lmbda function we created and click on +trigger

- Source is SQS , and then select our SQS we have craeted .
- Batch size : 5
- Batch window : 2

!(sample image)[project-12/image8.jpg]

### Now go to our MSK cluster -> view client information and copy the private endpoint

## Step 8 (Launch one SQS Queue with visibility timeout to 240 sec )

- If our API gateway is sending data in a high speed our lambda wont be able to work in that speed . We also have to make sure that the visibility time of SQS is higher - than the execution time of lambda
- Go to aws -> SQS -> create queue ->
- name : apitolambdaviaqsproject
- visibility timeout : 240 seconds
- keep all the other properties as it is and create it
- Go to aws - API Gateway -> HTTP ->
- API name : publishto lambdaproject , now click on Next , Next , select auto deploy and click on Next -> create
- Go to aws -> IAM -> Roels -> cretae roles -> use case : API Gateway -> Next -> Next -> Role Name : project demo and click on create role . Once it is created go inside it -> add permissions and attach AmazonSQSFullAccess to it . Now go back to Routes

- POST in the first box and in the next box , /publisher and click on create . Then click on that POST and click on Attach integration -> create integration ->
  integration type : Amazon Simple Queue Service
- integration action : SendMessage
- Queue URL : copy and paste the URL of our SQS
- Invocation role : copy and paste the arn of IAM role we created
- MessageBody : $request.body.MessageBody
- Now go to Advanced settings
- select the region as the region where our SQS is configured

## Step 9

- Test the integration , if works , then setup integration with AWS Lambda Producer
- For this go to the API Gateway that we created and then copy the invoke URL
- Paste that URL/publisher in postman , method : POST , type:JSON and then put some dummy json data send the request . Now go to sqs in aws , there click on the latest log -> Send and receive messages -> poll for messages -> Body . There we can see the message we send via postman

## Step 10

- Create an s3 bucket for data archival
- Now go to aws -> Kinesis -> create delivery stream ->
- Source : Direct PUT
- Destination : Amazon s3
- s3 bucket : click on browse and select the bucket that we have created
- After that click on create delivery stream

## Step 11 (Configure kinesis Firehose)

## Step 12 (Configure the Consumer Lambda Code )

- No go to aws lambda -> create a function ->
- Function name : producerlambdamskproject
- Runtime : python 3.8
- then create it . After that go to code and paste the following code there and after that click on deploy

```python
import base64
import boto3
import json

client = boto3.client('firehose')

def lambda_handler(event, context):
       print(event)
       for partition_key in event['records']:
              partition_value=event['records'][partition_key]
              for record_value in partition_value:
                     actual_message=json.loads((base64.b64decode(record_value['value'])).decode('utf-8'))
                            print(actual_message)
                            newImage = (json.dumps(actual_message)+'\n').encode('utf-8')
                            print(newImage)
                            response = client.put_record(
                                   DeliveryStreamName='here put Kinesis Delivery Stream Name',
                                   Record={
                                   'Data': newImage
                                   })

```

### Now go to lambda function we created -> click on add trigger

### Now go to lambda function we created -> configurations -> Edit -> edit the timeout time

### Now go to lambda function we created -> configurations -> Permissions -> Role name -> add permissions -> add the following policies

- AmazonVPCFullAccess
- AmazonMSKFullAccess
- AmazonKinesisFullAccess

## Step 13 create key pairs for first EC2 and then use it for the second EC2. For the public one -> click on Auto-assign a public IP

Launch an EC2 in a public subnet in same VPC as of MSK Cluster in a public subnet.
Launch an EC2 in private subnet in same VPC as of MSK Cluster in a private subnet.

## Step 14: Enter in public subnet , from there enter in private subnet.

- Here we cant directly connect with private EC2 , so first we connect with public EC2 and then through that we connect to private EC2
- First copy the public ip of public EC2 -> open winscp -> click on New Site and paste that ip in the Hot name box . username : ec2-user . Click on advanced -> Authentication and then select the pem file . Then it will give a notication saying COntinue connecting to an unknow server and add its host key to a cache : select no Now drag that pem file of private ec2 from our local machine to public EC2
- Now launch mobaxterm and connect with our public EC2
- first do ls to get the name of the pem file

```
-hmod 400 <name of the pem>     # cmod 400 thar.pem
ssh -i “thar.pem” ec2-ser@<private-ip-of-EC2>
sudo yum install java-1.8.0-openjdk
wget https://archive.apache.org/dist/kafka/2.8.1/kafka_2.12-2.8.1.tgz
tar -xvf kafka_2.12-2.8.1.tgz
```

- Add private ec2 security group and msk security group both way all traffic IPV4
- For that go to MSK cluster -> properties -> security groups applied ->edit inbound rules -> add rule
- Alltraffic
- source : security group of our private EC2
- Do the same for EC2 security group as well

```
sudo yum install java-1.8.0-openjdk
wget https://archive.apache.org/dist/kafka/2.8.1/kafka_2.12-2.8.1.tgz
tar -xvf kafka_2.12-2.8.1.tgz
cd kafka_2.12-2.8.1

bin/kafka-topics.sh --create --topic demo_testing2 --bootstrap-server {} --replication-factor 1 --partitions 2
```

## Step 15:

- Start kafka console consumer and check whether from Lambda messages are getting published in kafka topic or not

```
bin/kafka-console-consumer.sh --topic demo_testing2 --bootstrap-server {}
```

## Step 16:

- Add MSK Trigger from Consumer Lambda
