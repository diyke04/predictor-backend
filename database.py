import sqlalchemy as _sql
import sqlalchemy.orm  as _orm
import sqlalchemy.ext.declarative as _dbase


URL_DATABASE ='sqlite:///./predictor.db'

engine =_sql.create_engine(URL_DATABASE,connect_args={'check_same_thread':False})

SessionLocal =_orm.sessionmaker(autocommit=False,autoflush=False,bind=engine)

Base =_dbase.declarative_base()