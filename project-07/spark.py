import sys
from pyspark.sql import SparkSession
from pyspark import SparkContext
from pyspark.sql.types import *



spark = SparkSession \
        .builder \
        .appName("Oracle_to_snowflake_via_S3") \
        .getOrCreate()
        


def main():
    s3_bucket=sys.argv[1];
    s3_file=sys.argv[2];
    s3_location="s3a://{}/{}".format(s3_bucket,s3_file);
    iris = spark.read.format("csv").option("inferSchema","true").option("header","true").load(s3_location);
    ms=iris.groupBy("class").count()
    ms.coalesce(1).write.format("csv").option("header", "true").save("s3a://destinationbucketprocessed/{}".format(s3_file.split('.')[0]))
main()