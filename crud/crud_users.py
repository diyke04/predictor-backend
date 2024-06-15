from sqlalchemy.orm import Session
from models.user import User
from schemas.user import UserCreate,UserUpdateRole
from core.security import get_password_hash

def create_user(db: Session, user: UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = User(username=user.username, email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    print(db_user)
    return db_user

def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

from sqlalchemy.exc import NoResultFound

def update_user_role(db: Session, user_id: int, role: UserUpdateRole):
    try:
        user = db.query(User).filter(User.id == user_id).one()
        
        # Update the user's roles if the fields are provided
        if role.is_super_user is not None:
            user.is_super_user = role.is_super_user
        if role.is_admin is not None:
            user.is_admin = role.is_admin
        
        # Commit the changes to the database
        db.commit()
        db.refresh(user)
        
        return user
    except NoResultFound:
        # Handle the case where the user does not exist
        return None
