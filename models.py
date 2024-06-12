from database import Base
import datetime as _dt
import  sqlalchemy as _sql

class Matches(Base):
    __tablename__ ='matches'

    id =_sql.Column(_sql.Integer,primary_key=True,index=True)
    date=_sql.Column(_sql.String)
    away_team=_sql.Column(_sql.String(50))
    home_team=_sql.Column(_sql.String(50))
    away_team_score_prediction=_sql.Column(_sql.Integer)
    home_team_score_prediction=_sql.Column(_sql.Integer)
    away_team_score_ft=_sql.Column(_sql.Integer)
    home_team_score_ft=_sql.Column(_sql.Integer)
    result=_sql.Column(_sql.String(4))
    date_created = _sql.Column(_sql.DateTime,default=_dt.datetime.now())
    date_last_updated = _sql.Column(_sql.DateTime,default=_dt.datetime.now())



