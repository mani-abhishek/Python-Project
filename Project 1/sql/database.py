import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

username="root"
password="123456"
db_name="my_db"

#SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app.db"
#SQLALCHEMY_DATABASE_URL = "mysql+mysqlconnector://root:root@host.docker.internal:3306/sudharsan"

SQLALCHEMY_TRACK_MODIFICATIONS=True

#Local
# SQLALCHEMY_DATABASE_URL = "mysql+mysqlconnector://root:pass@localhost:3306/hzdb"
SQLALCHEMY_DATABASE_URL =  f"mysql+pymysql://{username}:{password}@localhost:3306/{db_name}"


#Docker
# SQLALCHEMY_DATABASE_URL = "mysql+mysqlconnector://root:123456@127.0.0.1:3306/sudharsan"
#SQLALCHEMY_DATABASE_URL = "mysql+mysqlconnector://fastApiUser:fastApi37Pass@0.0.0.0:3306/hzdb"
# SQLALCHEMY_DATABASE_URL = "mysql+mysqlconnector://hertzDBUserLatest:hzdb-123*@127.0.0.1:3306/hertzdblatest"
print("SQLALCHEMY_DATABASE_URL :: ", SQLALCHEMY_DATABASE_URL)

engine = create_engine(
    SQLALCHEMY_DATABASE_URL#, connect_args={"check_same_thread": False}
)

# sql lite in-memory database
# engine = create_engine('sqlite://')

SessionLocal = sessionmaker(autocommit=False, autoflush=True, bind=engine)

Base = declarative_base()
