import pyodbc

def get_connection():
    return pyodbc.connect(
        "DRIVER={SQL Server};"
        "SERVER=DESKTOP-2EPUQE6\SQLEXPRESS;"
        "DATABASE=BDUnion;"
        "UID=sa;"
        "PWD=root;"
    )
