from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import NoResultFound
from models.user import User
from schemas.user import UserCreate, UserUpdateRole
from core.config import RewardType
from core.security import get_password_hash
from reward.reward import reward_user

async def create_user(db: AsyncSession, user: UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = User(username=user.username, email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    await reward_user(user=db_user, reward_type=RewardType.USER_CREATION, db=db)
    return db_user

async def get_user_by_username(db: AsyncSession, username: str):
    result = await db.execute(select(User).filter(User.username == username))
    user = result.scalars().first()
    return user

async def get_user_by_email(db: AsyncSession, email: str):
    result = await db.execute(select(User).filter(User.email == email))
    user = result.scalars().first()
    return user

async def update_user_role(db: AsyncSession, user_id: int, role: UserUpdateRole):
    try:
        result = await db.execute(select(User).filter(User.id == user_id))
        user = result.scalars().one()

        if role.is_admin is not None:
            user.is_admin = role.is_admin

        await db.commit()
        await db.refresh(user)

        return user
    except NoResultFound:
        return None
