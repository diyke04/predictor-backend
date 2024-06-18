from sqlalchemy.orm import Session
from sqlalchemy.exc import NoResultFound
from models.user import User
from schemas.user import UserCreate,UserUpdateRole
from core.config import RewardType
from core.security import get_password_hash
from reward.reward import reward_user


async def create_user(db: Session, user: UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = User(username=user.username, email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    await reward_user(user=db_user,reward_type=RewardType.USER_CREATION,db=db)
    return db_user

async def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

async def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

async def update_user_role(db: Session, user_id: int, role: UserUpdateRole):
    try:
        user = db.query(User).filter(User.id == user_id).one()
        
        # Update the user's roles if the fields are provided
        if role.is_admin is not None:
            user.is_admin = role.is_admin
        
        # Commit the changes to the database
        db.commit()
        db.refresh(user)
        
        return user
    except NoResultFound:
        # Handle the case where the user does not exist
        return None
