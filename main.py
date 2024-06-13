from typing import List
from fastapi import FastAPI,Depends,HTTPException,status
from fastapi.security import OAuth2PasswordRequestForm
import auth as _auth
import schema as _schema
from sqlalchemy.orm import Session
import services as _services
from fastapi.middleware.cors import CORSMiddleware

app=FastAPI()

origins =[
" http://localhost:3000",
]

app.add_middleware(CORSMiddleware,allow_origins=origins,)


@app.get('/matches',response_model=List[_schema.Match])
async def get_all_matches(db:Session=Depends(_services.get_db)):
    return await _services.get_all_matches(db)

@app.get('/match',response_model=_schema.Match)
async def get_matchs(id,db:Session=Depends(_services.get_db)):
    return await _services.get_match(id=id,db=db)

@app.post('/create-match')
async def create_match(match: _schema.MatcheCreate,db:Session=Depends(_services.get_db)):
    return await _services.create_match(match=match,db=db)

@app.put('/update-match-result')
async def update_match_result(data:_schema.Match,db:Session=Depends(_services.get_db)):
    return await _services.update_match_result(data=data,db=db)

@app.put('/update-match-prediction')
async def update_match_prediction(data:_schema.Match,db:Session=Depends(_services.get_db)):
    return await _services.update_match_prediction(data=data,db=db)


@app.post('/create-user',response_model=_schema.User)
async def create_user(user:_schema.UserCreate,db:Session=Depends(_services.get_db)):
    return await _services.create_user(data=user,db=db)


@app.post('/api/token')
async def generate_token(form_data:OAuth2PasswordRequestForm=Depends(), db:Session=Depends(_services.get_db)):
    user =await _auth.authenticate_user(username=form_data.username,password=form_data.password,db=db)
    

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="INVALID CREDENTIALS")
    
    return await _auth.create_token(user=user)
