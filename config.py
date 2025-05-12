import os

class Config:
    DB_USER = os.getenv("DB_USER", "your_db_user")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "your_db_password")
    DB_NAME = os.getenv("DB_NAME", "your_db_name")
    DB_HOST = os.getenv("DB_HOST", "your_db_host")  # e.g., IP address or connection name
    DB_PORT = os.getenv("DB_PORT", "5432")

    SQLALCHEMY_DATABASE_URI = (
        f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
