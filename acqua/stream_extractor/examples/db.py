import os
from sqlalchemy import create_engine
from sqlalchemy import MetaData
from sqlalchemy import Table, Column, Integer, String, ARRAY
from sqlalchemy import select
from sqlalchemy.orm import sessionmaker

from dotenv import load_dotenv
load_dotenv()

conn_string = f"postgresql://{os.environ['POSTGRES_USERNAME']}:{os.environ['POSTGRES_PASSWORD']}@{os.environ['POSTGRES_URL']}/{os.environ['POSTGRES_DATABASE']}"

engine = create_engine(conn_string)
metadata = MetaData()

sector_table = Table(
    "news_companysector",
    metadata,
    Column('id', Integer, primary_key=True),
    Column('name', String(30)),
    Column('alternative_names', ARRAY(String))
)


Session = sessionmaker(bind=engine)
session = Session()
sectors = session.query(sector_table).all()
sectors_names = [[sector[1], *sector[2]] for sector in sectors]
