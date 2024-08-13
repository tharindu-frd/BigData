# MSK Connect

!(sample image)[image.jpg]

#### Kafka Connect is an open-source component of Apache Kafka that provides a framework for connecting with external systems such as databases , key-value , search indexes and file systems. However , manually running kafka connect cluster requires us to plan provision the required infrastructure , deal with cluster operations , and scale it in response to load changes . MSK connect allow us to configure and deploy a connector using Kafka Connect with a just few clicks

#### MSK Connect provisions the required resources and sets up the cluster . It continously monitors the health and delivery state of connectors , patches and manages the underlying hardware , and auto-scales connectors to match changes in throughput . As a result we can focus our resources on building applications rather than managing infrastructure .

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

!(sample image)[project-12/image3.jpg]

### Now click on subnet associations -> Edit subnet associations

!(sample image)[image4.jpg]

- Go to Route Tables -> create route table
- Name : private route table
- VPC : select the VPC that we have created
- After that click on Edit routes -> Add routes
- Destination : 0.0.0.0/0
- Target : igw - ( Here select the internet gateway we have created )
- Now click on subnet associations -> Edit associations

!(sample image)[project-12/image5.jpg]

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

### step 7:

- Open up the command prompt in our local machine and type 'wsl' and hit an enter to switch to wsl . Now run following commands

```
openssl genrsa -out rsa_key.pem 2048
openssl rsa -in rsa_key.pem -pubout -out rsa_key.pub
```

- These files contain keys that may contain spaces and new line characters which need to be removed. So run the following 2 commands

```
export SNOWFLAKE_PVT_KEY=$(echo `sed -e '2,$!d' -e '$d' -e 's/\n/ /g' rsa_key.pem`|tr -d ' ')
echo $SNOWFLAKE_PVT_KEY > rsa_key_p8.out
```

### step 8: Configure Snowflake:

- Goto snowflake and execute the following command . For the rsa_public_key , run the command 'cat rsa_key.pub' in the above WSL terminal and copy the output and paste it as the rsa_public_key

```sql
DROP DATABASE IF EXISTS RAMU;
Create database ramu;
alter user Satadru set rsa_public_key='';

desc user satadru;
use ramu;
show tables;
```

### Step 9 (create key pairs for first EC2 and then use it for the second EC2. For the public one -> click on Auto-assign a public IP )

- Launch an EC2 in a public subnet in same VPC as of MSK Cluster in a public subnet.
- Launch an EC2 in private subnet in same VPC as of MSK Cluster in a private subnet.
- Here we cant directly connect with private EC2 , so first we connect with public EC2 and then through that we connect to private EC2
- First copy the public ip of public EC2 -> open winscp -> click on New Site and paste that ip in the Hot name box . username : ec2-user . Click on advanced -> Authentication and then select the pem file . Then it will give a notication saying COntinue connecting to an unknow server and add its host key to a cache : select no Now drag that pem file of private ec2 from our local machine to public EC2
- Now launch mobaxterm and connect with our public EC2
- first do ls to get the name of the pem file

- Add private ec2 security group and msk security group both way all traffic IPV4
- For that go to MSK cluster -> properties -> security groups applied ->edit inbound rules -> add rule
- Alltraffic
- source : security group of our private EC2
- Do the same for EC2 security group as well

```
cmod 400 <name of the pem>     # cmod 400 thar.pem
ssh -i “thar.pem” ec2-ser@<private-ip-of-EC2>
sudo yum install java-1.8.0-openjdk
wget https://archive.apache.org/dist/kafka/2.8.1/kafka_2.12-2.8.1.tgz
tar -xvf kafka_2.12-2.8.1.tgz
```

-- Now inside that private EC2 install following

```

sudo yum install java-1.8.0-openjdk
wget https://archive.apache.org/dist/kafka/2.8.1/kafka_2.12-2.8.1.tgz
tar -xvf kafka_2.12-2.8.1.tgz
cd kafka_2.12-2.8.1
```

#### Go to MSK clusters and click on our cluster -> view client information -> copy the private endpoint and put it in the following <> next to bootstrap server

```
bin/kafka-topics.sh --create --topic demo_testing2 --bootstrap-server <> --replication-factor 1 --partitions 2
```

#### Create Custom plugins: For this click on the following link install the jar file locally . After that create a s3 bucket called connectordemoyt . Inside that bucket upload the jar file we downloaded .

https://mvnrepository.com/artifact/com.snowflake/snowflake-kafka-connector/1.5.0

#### Now go to aws -> MSK clusters -> Under MSK Connect we can see Custom plugins , click on that -> create a custom plugin . There browse and select the s3 we created . (we have to select the path of that jar file )

#### Now go to aws -> MSK clusters -> Under MSK Connect we can see Connectiors , just click on that -> click on create connector and there select the plugin we just created . Select our MSK clsuter as well . Under configuration paste the following code

```
connector.class=com.snowflake.kafka.connector.SnowflakeSinkConnector
tasks.max=8
topics=demo_testing2
snowflake.topic2table.map=demo_testing2:fake_data_real_time_demo
buffer.count.records=10000
buffer.flush.time=60
buffer.size.bytes=5000000
snowflake.url.name=
snowflake.user.name=
snowflake.private.key=  # this is the private key we generated earlier
snowflake.database.name=RAMU
snowflake.schema.name=PUBLIC
key.converter=com.snowflake.kafka.connector.records.SnowflakeJsonConverter
value.converter=com.snowflake.kafka.connector.records.SnowflakeJsonConverter
```

### IAM Role:s3--give s3 full access

### Trust Relationship--

{
"Version": "2012-10-17",
"Statement": [
{
"Effect": "Allow",
"Principal": {
"Service": "kafkaconnect.amazonaws.com"
},
"Action": "sts:AssumeRole",
"Condition": {
"StringEquals": {
"aws:SourceAccount": "Account ID"
}
}
}
]
}

Create a cloudwatch log group

## Connector Config:

## Test:

## Produce messages:

bin/kafka-console-producer.sh --topic demo_testing2 --bootstrap-server {}

## Consume messages:

bin/kafka-console-consumer.sh --topic demo_testing2 --bootstrap-server {}

## Destination:

select \* from ramu.public.fake_data_real_time_demo;

## Sample Data to Publish:

{"email":"wzanettinirp@stanford.edu","timestamp":1663420415,"event":"spamreport","gender":"Female","ip_address":"8.166.173.156"}
{"email":"pstegersrq@reddit.com","timestamp":1664321942,"event":"spamreport","gender":"Female","ip_address":"128.214.160.228"}
{"email":"avlahosrr@posterous.com","timestamp":1646024825,"event":"bounce","gender":"Female","ip_address":"147.51.176.231"}

---

---

---

---

---

---
