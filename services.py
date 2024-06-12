import database as _db
import sqlalchemy.orm as _orm
import models as _models
import schema as _schema
import datetime as _dt
import fastapi as _fastapi


async def get_all_matches(db:_orm.Session):
    match =db.query(_models.Matches).all()
    if not match:
        raise _fastapi.HTTPException(status_code=404, detail="Matches not found")
    return match

async def get_match(id: int, db: _orm.Session):
    match = db.query(_models.Matches).filter(_models.Matches.id == id).first()
    if not match:
        raise _fastapi.HTTPException(status_code=404, detail="Match not found")
    return match
    

async def create_match(match:_schema.MatcheCreate,db:_orm.Session):

    match_obj=_models.Matches(away_team=match.away_team,home_team=match.home_team,date=match.date)

    db.add(match_obj)
    db.commit()
    db.refresh(match_obj)
    return match_obj


async def update_match_result(data, db:_orm.Session):
    match_obj = db.query(_models.Matches).filter(_models.Matches.id==data.id).first()
    match_obj.home_team_score_ft=data.home_team_score_ft
    match_obj.away_team_score_ft=data.away_team_score_ft
    match_obj.date_last_updated =_dt.datetime.now()
   

    if match_obj.away_team_score_ft==match_obj.home_team_score_ft:
        match_obj.result ='Draw'

    elif match_obj.home_team_score_ft > match_obj.away_team_score_ft:
        match_obj.result='Home Win'
    else :
        match_obj.result ='Away Win'
    
    db.commit()
    db.refresh(match_obj)
    return _schema.Match.model_validate(match_obj)


async def update_match_prediction(data, db:_orm.Session):
    match_obj = db.query(_models.Matches).filter(_models.Matches.id==data.id).first()
    match_obj.away_team_score_prediction=data.away_team_score_prediction
    match_obj.home_team_score_prediction=data.home_team_score_prediction
    match_obj.date_last_updated =_dt.datetime.now()
    
    db.commit()
    db.refresh(match_obj)
    return _schema.Match.model_validate(match_obj)




def create_database():
    return _db.Base.metadata.create_all(bind=_db.engine)

def get_db():
    db =_db.SessionLocal()

    try:
        yield db

    finally:
        db.close()

    