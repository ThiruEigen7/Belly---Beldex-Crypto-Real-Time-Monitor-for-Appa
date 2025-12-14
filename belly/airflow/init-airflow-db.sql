-- Create Airflow database if it doesn't exist
CREATE DATABASE airflow
    WITH
    ENCODING = 'UTF-8'
    LC_COLLATE = 'C'
    LC_CTYPE = 'C'
    TEMPLATE = 'template0';
