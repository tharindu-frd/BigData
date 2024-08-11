#pip3 install boto3 -t.
#pip3 install aws-glue-schema-registry --upgrade --use-pep517 -t .
#pip install kafka-python -t .
import boto3
from time import sleep
from json import dumps
from kafka import KafkaProducer
from aws_schema_registry import DataAndSchema, SchemaRegistryClient
from aws_schema_registry.avro import AvroSchema
from aws_schema_registry.adapter.kafka import KafkaSerializer

session = boto3.Session(aws_access_key_id='{}', aws_secret_access_key='{}')

glue_client = session.client('glue', region_name='us-east-1')


# Create the schema registry client, which is a façade around the boto3 glue client
client = SchemaRegistryClient(glue_client,
                              registry_name='my-registry')

# Create the serializer
serializer = KafkaSerializer(client)

# Create the producer
producer = KafkaProducer(bootstrap_servers=['localhost:9092'],value_serializer=serializer)


# Our producer needs a schema to send along with the data.
#In this example we're using Avro, so we'll load an .avsc file.
with open('C:/Users/USER/PycharmProjects/kafka_python/user.avsc', 'r') as schema_file:
    schema = AvroSchema(schema_file.read())



#Send message data along with schema
data = {
    'name': 'Hello',
    'Age':45
}
#data={'Partiiton_no':2}
record_metadata =producer.send('glue_schema_bms', value=(data, schema)).get(timeout=10)   # topic_name : glue_schema_bms 
print(record_metadata.topic)
print(record_metadata.partition)
print(record_metadata.offset)