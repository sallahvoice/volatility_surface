import os
from dotenv import load_dotenv

load_dotenv()

db_host = os.getenv("DB_HOST") 
db_port = int(os.getenv("DB_PORT", "3306"))
db_user = os.getenv("DB_USER") 
db_password = os.getenv("DB_PASSWORD") 
db_name = os.getenv("DB_NAME") 
db_pool_size = int(os.getenv("DB_POOL_SIZE", "5"))
db_pool_name = os.getenv("DB_POOL_NAME")