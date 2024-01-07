import sqlite3
from flask import g

def connect_to_database():
    sql = sqlite3.connect(" /Users/katrinaalejo/Downloads/EcoConnect-1/ecoConn.db")
    sql.row_factory = sqlite3.Row
    return sql

def getDatabase():
    if not hasattr(g, "eco_db"):
        g.eco_db = connect_to_database()
    return g.eco_db