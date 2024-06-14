from db.base import Base
from db.session import engine

def create_database():
    return Base.metadata.create_all(bind=engine)


    