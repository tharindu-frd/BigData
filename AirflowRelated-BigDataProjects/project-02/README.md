# Automate loading data from S3 to Snowflake with email notification using airflow

!(sample image)[image.jpg]
sudo apt update
sudo apt install python3-pip
sudo apt install python3.10-venv
python3 -m venv airflow_snow_venv
source airflow_snow_venv/bin/activate
sudo pip install apache-airflow
pip install apache-airflow-providers-snowflake
pip install snowflake-connector-python
pip install snowflake-sqlalchemy
pip install apache-airflow-providers-amazon
airflow standalone
DROP DATABASE IF EXISTS city_database;
CREATE DATABASE IF NOT EXISTS city_database;
CREATE WAREHOUSE IF NOT EXISTS city_warehouse;
CREATE SCHEMA new_city_schema;
CREATE OR REPLACE STAGE city_database_yml.city_schema.snowflake_ext_stage_yml url="s3://airflow-snow-email-bucket/"
credentials=(aws_key_id='xxxxxxxxxxxx'
aws_secret_key='xxxxxxxxxx');
list @city_database_yml.city_schema.snowflake_ext_stage_yml;
CREATE OR REPLACE FILE FORMAT csv_format
TYPE = 'CSV'
FIELD_DELIMITER = ','
RECORD_DELIMITER = '\n'
SKIP_HEADER = 1;
