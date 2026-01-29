from contextlib import contextmanager
from mysql.connector import Error, pooling
from db.config import (db_host, db_port,
db_user, db_password, db_name, db_pool_size, db_pool_name)
from logger import get_logger

logger = get_logger(__file__)

def create_db_pool():
    try:
        return pooling.MySQLConnectionPool(
            
        )
    except Error as e:

_POOL = create_db_pool()

class DatabaseConnection:
    def __init__(self, pool):
        self.pool = pool

    @contextmanager
    def get_connection(self):

    @contextmanager
    def get_cursor()


database = DatabaseConnection(_POOL)