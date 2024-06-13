import database as _db
from sqlalchemy.orm import Session
import models as _models
import schema as _schema
from datetime import datetime
from fastapi import HTTPException,status
from passlib.hash import bcrypt


async def get_all_matches(db:Session):
    match =db.query(_models.Matches).all()
    if not match:
        raise HTTPException(status_code=404, detail="Matches not found")
    return match

async def get_match(id: int, db: Session):
    match = db.query(_models.Matches).filter(_models.Matches.id == id).first()
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    return match
    

async def create_match(match:_schema.MatcheCreate,db:Session):

    match_obj=_models.Matches(away_team=match.away_team,home_team=match.home_team,date=match.date)

    db.add(match_obj)
    db.commit()
    db.refresh(match_obj)
    return match_obj


async def update_match_result(data, db:Session):
    match_obj = db.query(_models.Matches).filter(_models.Matches.id==data.id).first()
    match_obj.home_team_score_ft=data.home_team_score_ft
    match_obj.away_team_score_ft=data.away_team_score_ft
    match_obj.date_last_updated =datetime.now()
   

    if match_obj.away_team_score_ft==match_obj.home_team_score_ft:
        match_obj.result ='Draw'

    elif match_obj.home_team_score_ft > match_obj.away_team_score_ft:
        match_obj.result='Home Win'
    else :
        match_obj.result ='Away Win'
    
    db.commit()
    db.refresh(match_obj)
    return _schema.Match.model_validate(match_obj)


async def update_match_prediction(data, db:Session):
    match_obj = db.query(_models.Matches).filter(_models.Matches.id==data.id).first()
    match_obj.away_team_score_prediction=data.away_team_score_prediction
    match_obj.home_team_score_prediction=data.home_team_score_prediction
    match_obj.date_last_updated =datetime.now()
    
    db.commit()
    db.refresh(match_obj)
    return _schema.Match.model_validate(match_obj)



async def create_user(data,db:Session):

    user = get_user_by_username(username=data.username,db=db)

    if user:
        raise HTTPException(status.HTTP_302_FOUND,detail="user with this username already exist.")
 
    user_obj =_models.User(username=data.username,password=bcrypt.hash(data.password))

    db.add(user_obj)
    db.commit()
    db.refresh(user_obj)
    return user_obj



def get_user_by_username(username:str,db:Session):
    return db.query(_models.User).filter(_models.User.username==username).first()

def create_database():
    return _db.Base.metadata.create_all(bind=_db.engine)

def get_db():
    db =_db.SessionLocal()

    try:
        yield db

    finally:
        db.close()

    