from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from pathlib import Path

# 获取后端根目录 (LifeLog/backend)
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DEFAULT_DATA_DIR = BASE_DIR / "data"
DEFAULT_DATA_DIR.mkdir(exist_ok=True)

# 默认使用 SQLite，生产环境可通过环境变量切换到 MySQL
DB_TYPE = os.getenv("DB_TYPE", "sqlite")
if DB_TYPE == "mysql":
    DB_USER = os.getenv("DB_USER", "root")
    DB_PASS = os.getenv("DB_PASS", "root")
    DB_HOST = os.getenv("DB_HOST", "db")
    DB_NAME = os.getenv("DB_NAME", "lifelog")
    SQLALCHEMY_DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}"
else:
    # 优先使用环境变量，否则在 Docker 中强行使用 /app/data/lifelog.db
    if os.path.exists("/app"):
        SQLITE_PATH = os.getenv("SQLITE_DB_PATH", "/app/data/lifelog.db")
    else:
        SQLITE_PATH = os.getenv("SQLITE_DB_PATH", str(DEFAULT_DATA_DIR / "lifelog.db"))
    
    SQLALCHEMY_DATABASE_URL = f"sqlite:///{SQLITE_PATH}"

import sqlite3
from sqlalchemy.engine import Engine
from sqlalchemy import event

# @event.listens_for(Engine, "connect")
# def set_sqlite_pragma(dbapi_connection, connection_record):
#     if type(dbapi_connection) is sqlite3.Connection:
#         cursor = dbapi_connection.cursor()
#         cursor.execute("PRAGMA journal_mode=WAL")
#         cursor.execute("PRAGMA synchronous=NORMAL")
#         cursor.close()

if SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
    print(f"Creating SQLite engine with URL: {SQLALCHEMY_DATABASE_URL}")
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
    )
else:
    print(f"Creating SQL engine with URL: {SQLALCHEMY_DATABASE_URL}")
    engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
