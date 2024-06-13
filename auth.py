from services import get_user_by_username
from sqlalchemy.orm import Session
from models import User as user_model
from schema import User as user_schema
import jwt as _jwt
from datetime import datetime,timedelta

JWT_SECRET ="JWT_secret_key"
ALGORITHIM ='HS256'
JWT_EXPIRATION_MINUTES =120

async def authenticate_user(username:str,password:str,db:Session):
    
    user = get_user_by_username(username=username,db=db)

    if not user:
        return False
    if not user.verify_password(password):
        return False

    return user

async def create_token(user:user_model):
    user_obj = user_schema.model_validate(user)

    payload={
        "user":str(user_obj),
        'expires':str(datetime.now()+ timedelta(minutes=JWT_EXPIRATION_MINUTES))
    }

    token =_jwt.encode(payload=payload,key=JWT_SECRET,algorithm=ALGORITHIM)

    return dict(access_token=token , token_type='bearer')


async def decode_token(token):
    return _jwt.decode(token.access_token,key=JWT_SECRET,algorithms=ALGORITHIM)
   