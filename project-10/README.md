# AWS Managed Streaming for Kafka (MSK)

### Step 1 : Cretae VPC -- Name -- virtual-private-cloud IPv4 CIDR -- 10.0.0.0/16 | Host address range -- 10.0.0.1 - 10.0.255.254

### Step 2 : Create 2 public subnets

- Public-Subnet-A--10.0.0.0/24
- Host address range -- 10.0.0.1 - 10.0.0.254
- Public-Subnet-B--10.0.1.0/24
- Host address range -- 10.0.1.1 - 10.0.1.254

### Step 3 ( Here we dont have to do anything , just to see )

-Check the default route table -- you will see the above 2 subnets have not been explicitly associated with any route tables and are therefore associated with the main route table.

### Step 4 :Create a IGW & connect with VPC

### Step 5:

- Go to Internet Gateways and click on create gateway
- Name : myigw and then click on create gate way . Now go to that gateway we created and click on Actions and then select Attach to VPC . There select the vpc that we have created .
- Now go to Route tables and then select the one for our VPC that we created -> select Routes and then click on Edit routes
- Destination : 0.0.0.0/0
- Target : igw- ( Here select our igw we created )

### Step 6:

- Launch MSK Cluster just give it a name and select Provisioned as the cluster type , Broker type : kafka.t3.small , Number of zones :2 , Amazon EBS Storage per broker : 1 GB , select vpc we created , now select the 2 subnets we created with their zones , unauthorised access allowed , plaintext enxryption (keep security group as it is)

### Step 7: ( we use this EC2 to produce data and consume data )

- Launch Linux EC2 , here select the vpc that we created and select the subnet B ,In the list Auto-assign Public IP choose Enable.. Once we created the EC2 , click on that and go to security groups - > edit inbound rules
- Type: All traffic
- source : This must be the security group of our MSK cluster - Type : All traffic | source : anywher ipv4

- Now go to the MCK cluster and go to security groups -> edit inbound rules
- Type : All traffic
- source : security group of our Ec2

### Step 8: ( Now use mobaxterm to connect to the EC2 that we created. Here we have to isntall the kafka version that we have selected when we creating the MCK cluster )

```
sudo yum install java-1.8.0-openjdk
wget https://archive.apache.org/dist/kafka/2.8.1/kafka_2.12-2.8.1.tgz
tar -xvf kafka_2.12-2.8.1.tgz
cd kafka_2.12-2.8.1
```

- To get the URL for our MCK cluster -> go to MCK cluster - > View client information ->under private endpoint we can see the 2 URLs . Select the one with respect to the plain text

```
                        bin/kafka-topics.sh --create --topic demo_testing2 --bootstrap-server {Put the MSK bootstrap server URLs here} --replication-factor 1 --partitions 1

                        bin/kafka-topics.sh --create --topic helloworld --bootstrap-server {Put the MSK bootstrap server URLs here}  --replication-factor 1 --partitions 1
```

#### Start the kafka Producer

```
                    bin/kafka-console-producer.sh --topic demo_testing2 --bootstrap-server {Put the MSK bootstrap server URLs here}
```

#### In a new console start the kafka consumer (in a new session in mobaxterm)

```
           cd kafka_2.12-2.8.1
                bin/kafka-console-consumer.sh --topic helloworld --bootstrap-server {Put the MSK bootstrap server URLs here}
```

### Step 9 (Open up a new session in mobaxterm . Here we gonna install confluent in our EC2 so we can publish messages using the rest api )

- Install confluent kafka within kafka_2.12-2.8.1

```
        wget  http://packages.confluent.io/archive/5.1/confluent-5.1.2-2.11.zip
        unzip confluent-5.1.2-2.11.zip
        ls
        export CONFLUENT_HOME=/home/ec2-user/kafka_2.12-2.8.1/confluent-5.1.2
        export PATH=$PATH:$CONFLUENT_HOME/bin

```

- (Note , if installing confluent kafka , where kafka is installed (i.e. in /home/ec2-user) , then CONFLUENT_HOME should be -- /home/ec2-user/confluent-5.1.2)

```
        vi  confluent-5.1.2/etc/kafka-rest/kafka-rest.properties
```

- make the following changes
- bootstrap.servers = PLAINTEDT://<URL of MCK clsuter we copied >:9092 , PLAINTEDT://<second URL of MCK clsuter  >:9092

### Step 10 (Start Kafka Rest , run following in mobaxterm)

```
/home/ec2-user/kafka_2.12-2.8.1/confluent-5.1.2/bin/kafka-rest-start
/home/ec2-user/kafka_2.12-2.8.1/confluent-5.1.2/etc/kafka-rest/kafka-rest.properties
```

- Url to post messages using Kafka rest API--
- http://{Put your cleint machine's Public IP here}:8082/topics/demo_testing2
- Content-Type: application/vnd.kafka.json.v2+json

## Sample Message:

{"records":[{"value":{"name": "testUser"}}]}

## Start consumer to see the messages:

```
cd kafka_2.12-2.8.1
bin/kafka-console-consumer.sh --topic demo_testing2 --bootstrap-server {Put the MSK bootstrap server URLs here}
```

!(sample image)[image.jpg]
