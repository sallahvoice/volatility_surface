from pathlib import Path
import mysql.connector
from db.config import (db_host, db_port,
db_user, db_password, db_name, db_pool_size, db_pool_name)
from logger import get_logger

logger = get_logger(__file__)

def run_migration():
    migration_dir = Path(__file__).parent / "migrations"
    mysql_file = migration_dir / "001_something_table.sql"

    conn = mysql.connector.connect(
        db_host=db_host,
        db_port=db_port,
        db_user=db_user,
        db_password=db_password,
        db_name=db_name
    )

    cursor = conn.cursor()

    try:
        with open(mysql_file) as f:
            statement = f.read()
            if statement:
                cursor.execute(statement)
        logger.info("completed migration : %s", mysql_file.name)
    except FileNotFoundError as e:
        logger.error("file not found: %s", e)
        raise
    except Exception as e:
        logger.error("migration error: %s", e)
        raise

    conn.commit()
    cursor.close()
    conn.close()