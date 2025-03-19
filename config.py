import pyodbc

def get_connection():
    return pyodbc.connect(
        "DRIVER={SQL Server};"
        "SERVER=AMD5;"
        "DATABASE=BDUnion;"
        "UID=sa;"
        "PWD=12345;"
    )
