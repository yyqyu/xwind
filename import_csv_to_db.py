import csv
import pandas
from sqlalchemy import create_engine
import psycopg2 as pg
import pandas.io.sql as psql

# Python helper file to setup initial database (converting various CSV files to databases)
# Databases will be maintained using a dedicated interface on xwind.app

# Open CSV file using pandas library
df = pandas.read_csv("database/airports.csv")

# Creating a connection to the SQL database using SQL Alchemy
sql_engine = create_engine('postgresql://ohbzghuvifbqji:98678bba7c0ad4692d193d6c97d03c372a1e1de1637bb0d4196e6dfa7e2a6b99@ec2-52-207-74-100.compute-1.amazonaws.com:5432/d5gb21to36p7kt', echo=False)

connection = sql_engine.raw_connection()

# Copying CSV file into the right table in the database
df.to_sql("airports", sql_engine, if_exists='append', index=False)




