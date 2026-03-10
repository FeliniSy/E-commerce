from psycopg2 import pool
from utils.settings import settings

connection_pool = pool.ThreadedConnectionPool(
    minconn=5,
    maxconn=50,
    dsn=settings.DB_URL
)

def get_connection():
    return connection_pool.getconn()

def release_connection(conn):
    connection_pool.putconn(conn)