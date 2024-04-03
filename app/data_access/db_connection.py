import psycopg2
from psycopg2 import pool
import os
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv('DB_HOST')
DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_PORT = os.getenv('DB_PORT')


class Database:
    _connection_pool = None

    @staticmethod
    def initialise(**kwargs):
        Database._connection_pool = psycopg2.pool.SimpleConnectionPool(minconn=1, maxconn=10, **kwargs)

    @staticmethod
    def get_connection():
        return Database._connection_pool.getconn()

    @staticmethod
    def return_connection(connection):
        Database._connection_pool.putconn(connection)

    @staticmethod
    def close_all_connections():
        Database._connection_pool.closeall()

# Initialize the connection pool
Database.initialise(database=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST)

