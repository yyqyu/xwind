import csv
import pandas
from sqlalchemy import create_engine

# Python helper file to setup initial database (converting various CSV files to databases)
# Databases will be maintained using a dedicated interface on xwind.app

# Open CSV file using pandas library
df = pandas.read_csv("database/airports.csv")

# Creating a connection to the SQL database using SQL Alchemy
sql_engine = create_engine('sqlite:///database/xwind.db', echo=False)
connection = sql_engine.raw_connection()

# Copying CSV file into the right table in the database
df.to_sql("airports", connection, if_exists='append', index=False)




