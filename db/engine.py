from contextlib import contextmanager
from mysql.connector import Error, pooling
from db.config import (db_host, db_port,
db_user, db_password, db_name, db_pool_size, db_pool_name)
from logger import get_logger

logger = get_logger(__file__)

def create_db_pool():
    try:
        return pooling.MySQLConnectionPool(
            db_host=db_host,
            db_port=db_port,
            db_user=db_user,
            db_password=db_password,
            db_name=db_name,
            db_pool_size=db_pool_size,
            db_pool_name=db_pool_name
        )
    except Exception as e:
        logger.info("failed to create database pool: %s", e)


_POOL = create_db_pool()


class DatabaseConnection:
    def __init__(self, pool):
        self.pool = pool

    @contextmanager
    def get_connection(self):
        conn = None
        try:
            conn = self.pool.get_connection()
            yield conn
            conn.commit()
        except Exception as e:
            if conn:
                conn.rollback()
            logger.info("database error: %s", e)
            raise
        finally:
            if conn and conn.is_connected():
                conn.close()

    @contextmanager
    def get_cursor(self, dictionary=False):
        with self.get_connection() as conn:
            cursor = conn.cursor(dictionary=dictionary)
            try:
                yield cursor
            finally:
                cursor.close()


database = DatabaseConnection(_POOL)