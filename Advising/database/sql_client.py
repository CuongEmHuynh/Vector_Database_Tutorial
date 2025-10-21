import numpy as np
import pyodbc
import pandas as pd

SERVERDB="192.168.6.54"
USERNAME="sa"
PASSWORD="p@ssw0rd789"

# sql_client.py
import pyodbc

def get_connection():
    conn = pyodbc.connect(
        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        f"SERVER={SERVERDB};"
        f"DATABASE=CoVan;"
        f"UID={USERNAME};PWD={PASSWORD}"
    )
    return conn

def  fetch_data(connection):
    df = pd.read_sql(''' SELECT FirstName, LastName , StudentCode, Email, SN.Notes, SN.CreateDate as N'Ngày tạo ghi chú' From Students S
LEFT JOIN StudentNotes SN ON  S.Id = SN.StudentId
order by SN.CreateDate desc ''', connection)
    return df

if __name__ == "__main__":
    # Test the database connection
    try:
        connection = get_connection()
        data = fetch_data(connection)
        print(data.head()) 
        print("Connection successful!")
        connection.close()
    except Exception as e:
        print(f"Connection failed: {e}")