import os
from urllib.parse import quote_plus
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY")

    password = quote_plus(os.getenv("MYSQL_PASSWORD"))

    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{os.getenv('MYSQL_USER')}:"
        f"{password}@"
        f"{os.getenv('MYSQL_HOST')}:"
        f"{os.getenv('MYSQL_PORT')}/"
        f"{os.getenv('MYSQL_DATABASE')}"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False