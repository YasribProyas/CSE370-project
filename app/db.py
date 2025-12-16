import os
from mysql.connector import Error, pooling

from dotenv import load_dotenv
load_dotenv()

dbconfig = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', ''),
    'database': os.getenv('DB_NAME', 'havnhut')
}

connection_pool = None

def init_connection_pool():
    global connection_pool
    try:
        connection_pool = pooling.MySQLConnectionPool(
            pool_name="havnhut_pool",
            pool_size=3,
            pool_reset_session=True,
            **dbconfig
        )
        print("Connection pool created")
    except Error as e:
        print(f"Error creating connection pool: {e}")


def get_db_connection():
    try:
        if connection_pool is None:
            init_connection_pool()
        if connection_pool is not None:
            return connection_pool.get_connection()
        
    except Error as e:
        print(f"Error getting connection from pool: {e}")
        return None

def execute_query(query, params=None, fetch=False):
    connection = get_db_connection()
    if connection is None:
        return None
    
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute(query, params or ())
        if fetch:
            result = cursor.fetchall()
            return result
        else:
            connection.commit()
            return cursor.lastrowid
        
    except Error as e:
        print(f"Database error: {e}")
        connection.rollback()
        return None
    finally:
        cursor.close()
        connection.close()
