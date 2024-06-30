from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordRequestForm

from crud import crud_users
from schemas.user import UserCreate, User,UserUpdateRole,LoginUser
from core.security import verify_password, create_access_token
from db.session import get_db
from api.dependency import get_current_user

router = APIRouter()

@router.post("/register", response_model=User)
async def register_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user_username = await crud_users.get_user_by_username(db, username=user.username)
    db_user_email =await crud_users.get_user_by_email(db=db,email=user.email)
    if db_user_username:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    if db_user_email:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    return await crud_users.create_user(db=db, user=user)

@router.post("/token")
async def login_user(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    user = await crud_users.get_user_by_username(db, username=form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token = create_access_token(data={"sub": user.username,"id":user.id})
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/login")
async def login_user(form_data:LoginUser, db: AsyncSession = Depends(get_db)):
    user = await crud_users.get_user_by_username(db, username=form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token = create_access_token(data={"sub": user.username,"id":user.id})
    return {"access_token": access_token, "token_type": "bearer"}


@router.put("/user-role", response_model=User)
async def update_user_role(role: UserUpdateRole, db: Session = Depends(get_db),id:int=Depends(get_current_user)):

    return await crud_users.update_user_role(user_id=id,role=role,db=db)
