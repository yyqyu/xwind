import csv
import pandas
from sqlalchemy import create_engine
import psycopg2 as pg
import pandas.io.sql as psql

# Python helper file to setup initial database (converting various CSV files to databases)
# Databases will be maintained using a dedicated interface on xwind.app

# Open CSV file using pandas library
df = pandas.read_csv("database/runways.csv")

# Creating a connection to the SQL database using SQL Alchemy
sql_engine = create_engine('postgres://yslseapkhkqvfs:1296eb1622d1fc4fdc7864b5109102138cb7c3092199afdc7b747e5fd0b36bde@ec2-54-221-214-183.compute-1.amazonaws.com:5432/dau286g9ftm2ei', echo=False)

connection = sql_engine.raw_connection()

# Copying CSV file into the right table in the database
df.to_sql("runways", sql_engine, if_exists='append', index=False)




