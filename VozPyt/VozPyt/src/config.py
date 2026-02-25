import os
from dotenv import load_dotenv

load_dotenv(encoding='utf-8')

class Config:
    @staticmethod
    def get_db_params():
        return {
            'host': os.getenv('DB_HOST'),
            'database': os.getenv('DB_NAME'),
            'user': os.getenv('DB_USER'),
            'password': os.getenv('DB_PASSWORD'),
            'port': os.getenv('DB_PORT')
        }