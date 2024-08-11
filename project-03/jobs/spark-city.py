############ Here we gonna write our apache spark script ##########

from pyspark.sql import SparkSession
from config import configuration
from pyspark.sql.types import StructType, StructField, StringType, IntegerType,TimestampType,DoubleType
from pyspark.sql.functions import col, from_json
from pyspark.sql import DataFrame



## https://mvnrepository.com/artifact/org.apache.spark/spark-sql-kafka-0-10  
## Go to the above link and click on the  version that we put under requirements.txt . Here we are using pyspark==3.5.0 . So click on 3.5.0 . There we can get the group ID :  org.apache.spark and the artifact Id :  spark-sql-kafka-0-10_2.13   , version :  3.5.0


### https://mvnrepository.com/artifact/org.apache.hadoop/hadoop-aws/3.3.1
## <groupId>org.apache.hadoop</groupId>
##   <artifactId>hadoop-aws</artifactId>
##   <version>3.3.1</version>
def main():
       spark = SparkSession.builder.appName("SamrtCityStreaming)")\
       .config("spark.jars.packages",
               "org.apache.spark:spark-sql-kafka-0-10)2.13:3.5.0",
               "org.apache.hadoop:hadoop-aws:3.3.1",
               "com.amazonaws:aws-java-sdk:1.11.469")\
       .config("spark.hadoop.fs.s3s.impl","org.apache.hadoop.fs.s3a.S3FileSystem")\
       .config("spark.hadoop.fs.s3a.access.key",configuration.get('AWS_ACCESS_KEY'))\
       .config("spark.hadoop.fs.s3a.secret.key",configuration.get('AWS_SECRET_KEY'))\
       .config('spark.hadoop.fs.s3a.aws.credentials.provider','org.apache.hadoop.fs.s3a.impl.SimpleAWSCredentialsProvider').getOrCreate()


       ### Afjust the log level to minimize the console output on executor 
       spark.sparkContext.setLogLevel('WARN')

       # vehicle schema
       vehicleSchema = StructType([
              StructField("id",StringType(),True),
              StructField("deviceId",StringType(),True),
              StructField("timestamp",TimestampType(),True),
              StructField("location",StringType(),True),
              StructField("speed",DoubleType(),True),
              StructField("directions",StringType(),True),
              StructField("make",StringType(),True),
              StructField("model",StringType(),True),
              StructField("year",IntegerType(),True),
              StructField("fuelType",StringType(),True),


       ])

       #gps schema 
       gpsSchema = StructType([
              StructField("id",StringType(),True),
              StructField("deviceId",StringType(),True),
              StructField("timestamp",TimestampType(),True),
              StructField("speed",DoubleType(),True),
              StructField("directions",StringType(),True),
              StructField("vehicleType",StringType(),True),

       ])

       #trafficSchema
       trafficSchema = StructType([
              StructField("id",StringType(),True),
              StructField("deviceId",StringType(),True),
              StructField("cameraId",StringType(),True),
              StructField("location",StringType(),True),
              StructField("timestamp",TimestampType(),True),
              StructField("snapshot",StringType(),True),

       ])


       weatherSchema = StructType([
              StructField("id",StringType(),True),
              StructField("deviceId",StringType(),True),
              StructField("timestamp",TimestampType(),True),
              StructField("location",StringType(),True),
              StructField("temperature",DoubleType(),True),
              StructField("weatherCondition",StringType(),True),
              StructField("precipitation",DoubleType(),True),
              StructField("windSpeed",DoubleType(),True),
              StructField("humidity",IntegerType(),True),
              StructField("airQualityIndex",DoubleType(),True),

       ])
       


       emergencySchema = StructType([
              StructField("id",StringType(),True),
              StructField("deviceId",StringType(),True),
              StructField("incidentId",StringType(),True),
              StructField("type",StringType(),True),
              StructField("timestamp",TimestampType(),True),
              StructField("location",StringType(),True),
              StructField("status",StringType(),True),
              StructField("description",StringType(),True),

       ])



       def read_kafka_topic(topic, schema):
              return (spark.readStream
                     .format('kafka')
                     .option('kafka.bootstrap.servers', 'broker:29092')
                     .option('subscribe', topic)
                     .option('startingOffsets', 'earliest')
                     .load()
                     .selectExpr('CAST(value AS STRING)')
                     .select(from_json(col('value'), schema).alias('data'))
                     .select('data.*')
                     .withWatermark('timestamp', '2 minutes')
              )
       

       def streamWriter(input: DataFrame , checkpointFolder,output):
              return (input.writeStream
                      .format('parquet')
                      .option('checkpointLocation',checkpointFolder)
                      .option('path',output)
                      .outputMode('append')
                      .start()
                      
                      )


       
       vehicleDF = read_kafka_topic('vehicle_data',vehicleSchema).alias('vehicle')
       gpsDF = read_kafka_topic('gps_data',gpsSchema).alias('gps')
       trafficDF = read_kafka_topic('traffic_data',trafficSchema).alias('traffic')
       weatherDF = read_kafka_topic('weather_data',weatherSchema).alias('weather')
       emergencyDF = read_kafka_topic('emergency_data',emergencySchema).alias('emergency')



       ## join all the dfs with id and timestamp
       ## spark-stream-data : this is the name of the s3 bucket we created 
       query1 = streamWriter(vehicleDF,'s3a://spark-stream-data/checkpoints/vehicle_data','s3a://spark-stream-data/data/vehicle_data')
       query2 =streamWriter(gpsDF,'s3a://spark-stream-data/checkpoints/gps_data','s3a://spark-stream-data/data/gps_data')
       query3 =streamWriter(trafficDF,'s3a://spark-stream-data/checkpoints/vehicle_data','s3a://spark-stream-data/data/vehicle_data')
       query4 =streamWriter(weatherDF,'s3a://spark-stream-data/checkpoints/weather_data','s3a://spark-stream-data/data/weather_data')
       query5 =streamWriter(emergencyDF,'s3a://spark-stream-data/checkpoints/emergency_data','s3a://spark-stream-data/data/emergency_data')

       # now all of those queries will be run parallely
       query5.awaitTermination()



if __name__ == "__main__":
       main()