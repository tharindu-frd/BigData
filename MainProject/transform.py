from pyspark.sql import SparkSession
from pyspark import SparkContext
from pyspark.sql.types import *


spark = SparkSession \
        .builder \
        .appName("airflow_with_emr") \
        .getOrCreate()
        


def main():
    # S3 location of the JSON data
    s3_input_location = "s3://data-archival/output/"
    s3_output_location = "s3://dataarchival/output_folder/"

    # Read JSON data from S3
    df = spark.read.format("json").load(s3_input_location)

    # Show the DataFrame schema to understand its structure
    df.printSchema()

    # Drop the last column (assuming it's the last column in the schema)
    columns = df.columns
    if columns:
        df = df.drop(columns[-1])

    # Save DataFrame to Parquet format in S3
    df.write.format("parquet").mode('overwrite').save(s3_output_location)

    
