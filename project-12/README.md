#### ( This is the continuation of project-11) : Now we have seen the producer side in project-11 . Now lets see consumer side. Where whenever messges are sent to our MSK clsuter , an lambda function should be triggered and perform some tasks .

# Using Amazon MSK as an event source for AWS Lambda

!(sample image)[image1.jpg]

### For Amazon MSK to invoke lmabda , we must ensure that there is a NAT Gateway running in the public subnet of each region .

### A NAT Gateway (Network Address Translation Gateway) is a managed service in AWS that allows instances in a private subnet to access the internet or other AWS services while keeping those instances private and secure. Here's a detailed explanation of its purpose, how it works, and its use cases:

### What is a NAT Gateway?

- A NAT Gateway is a managed AWS service that enables instances in a private subnet within a Virtual Private Cloud (VPC) to initiate outbound traffic to the internet, while preventing unsolicited inbound traffic from the internet. It performs network address translation (NAT) to route traffic between the private instances and the external network.

### How It Works

- Outbound Traffic: When an instance in a private subnet needs to access the internet (e.g., to download software updates or access external services), it sends traffic to the NAT Gateway.
- The NAT Gateway translates the private IP address of the instance to a public IP address and forwards the request to the internet.
- Inbound Traffic: Responses from the internet are routed back to the NAT Gateway, which then translates the public IP address back to the private IP address and forwards the response to the originating instance.
- Managed Service: AWS manages the NAT Gateway, including scaling, availability, and maintenance. This reduces the operational burden compared to managing a NAT instance yourself.

!(sample image)[image2.jpg]

### Step 1:

- Cretae VPC -- Name -- virtual-private-cloud-lambda IPv4 CIDR -- 11.0.0.0/16
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

- Step 3 (Create an IGW and attach with VPC)
- Go to Internet Gateway -> Create internet gateway - > Once we crated it , click on that , then click on Attach to a vpc , and then select the VPC that we have created

### Step 4:

- Create 2 route tables 1 for Public subnets and 1 for Private subnets
- (Attach IGW with Public route tables)

- Go to Route Tables -> create route table -
  Name : public route table
- VPC : select the VPC that we have created
- After that click on Edit routes -> Add routes
- Destination : 0.0.0.0/0
- Target : igw - ( Here select the internet gateway we have created )

### Now click on subnet associations

!(sample image)[image3.jpg]

### Now click on subnet associations -> Edit subnet associations

!(sample image)[image4.jpg]

- Go to Route Tables -> create route table
- Name : private route table
- VPC : select the VPC that we have created
- After that click on Edit routes -> Add routes
- Destination : 0.0.0.0/0
- Target : igw - ( Here select the internet gateway we have created )
- Now click on subnet associations -> Edit associations

!(sample image)[image5.jpg]

### Step 5 : (Create NAT Gateway in public subnet and attach with Private Subnet route table )

Now go to NAT Gateway -> create NAT Gateway  
 Name : demoytlambdatrigger
Subnet : selct public subnet A lambda
connectivity type : public
click on alocate elastic Ip
Now go back to route tables -> click on private route tables -> Edit routes -> Add route ->
Destinations : 0.0.0.0/0
Target : select the NAT gateway we have created

### Step 6:

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

### Step 7 (create key pairs for first EC2 and then use it for the second EC2. For the public one -> click on Auto-assign a public IP )

- Launch an EC2 in a public subnet in same VPC as of MSK Cluster in a public subnet.
- Launch an EC2 in private subnet in same VPC as of MSK Cluster in a private subnet.
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

### Step 8:

- Add private ec2 security group and msk security group both way all traffic IPV4
- For that go to MSK cluster -> properties -> security groups applied ->edit inbound rules -> add rule
- Alltraffic
- source : security group of our private EC2
- Do the same for EC2 security group as well

### Step 9:

- Now go to aws lmabda -> create function
- Function Name : any name
- Runtime: python 3.9
- create it -> then go to code

!(sample image)[image7.jpg]

```python
import base64
import boto3
import json

def lambda_handler(event, context):
    # TODO implement
    print(event)
    for partition_key in event['records']:
        partition_value=event['records'][partition_key]
        for record_value in partition_value:
             print((base64.b64decode(record_value['value'])).decode())

```

### Now go to configurations -> Edit -> Edit the time out so we wont be having any time out issues

### Now go to configurations -> permissions- > click on Role name -> permissions -> add permission -> Attach following policies

- AWSLambdaMSKExecutionRole
- AmazonVPCFullAccess

### Now go to aws lmbda function we created and click on +trigger

- select : msk as source
- MSK cluster : select the cluster that we created
- Batch size : 10
- Batch window : 5
- topic name : demo_testing2

!(sample image)[image8.jpg]

### Now go to our MSK cluster -> view client information and copy the private endpoint

### Now go to mobaxterm

```
cd kafka_2.12-2.8.1
bin/kafka-topics.sh --create --topic demo_testing2 --bootstrap-server --replication-factor 1 --partitions 2 # bootstrap server -- here paste first url , second url of our MSK cluster

bin/kafka-console-producer.sh --topic demo_testing2 --bootstrap-server <public ip -1of cluster , public-ip-2 of our cluster>
```

### Open up a anothe mobaxterm session and connect to the private EC2 via pulib and do the same thing

```
cd kafka_2.12-2.8.1
bin/kafka-console-consumer.sh --topic demo_testing2 --bootstrap-server
```

# bootstrap server -- here paste first url , second url of our MSK cluster

!(sample image)[image9.jpg]

### Now in the first mobaxterm session our consumer is running and in the second session our producers is running .

### Now add the trigger

### Now when we type anything in the producer window in mobaxterm that can be seen in the consumer window and also when 10 messages are sent that will also trigger the lambda as well. To see that go to Monitor in lambda -> view cloud watch logs
