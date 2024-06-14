from services import get_user_by_username,get_db
from fastapi import Depends,HTTPException,status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
import models as _model
import schema as _schema
import jwt as _jwt
from datetime import datetime,timedelta

JWT_SECRET ="JWT_secret_key"
ALGORITHIM ='HS256'
JWT_EXPIRATION_MINUTES =120

oauth2schema=OAuth2PasswordBearer(tokenUrl='/api/token')

async def authenticate_user(username:str,password:str,db:Session):
    
    user = get_user_by_username(username=username,db=db)

    if not user:
        return False
    if not user.verify_password(password):
        return False

    return user

async def create_token(user:_model):
    user_obj = _schema.User.model_validate(user)

    payload={
        "user":user_obj.model_dump(),
        'expires':str(datetime.now()+ timedelta(minutes=JWT_EXPIRATION_MINUTES))
    }

    token =_jwt.encode(payload=payload,key=JWT_SECRET,algorithm=ALGORITHIM)

    return dict(access_token=token , token_type='bearer')


async def decode_token(token:str):
    return _jwt.decode(token,key=JWT_SECRET,algorithms=ALGORITHIM)
   
async def get_current_user(token:str=Depends(oauth2schema),db:Session=Depends(get_db)):
    try:
        payload= await decode_token(token)
        user =db.query(_model.User).get(payload['user']['id'])
        
    except:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED,detail=" Invalid username or Password")
    
    return _schema.User.model_validate(user)
    
