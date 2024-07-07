from sqlalchemy.ext.asyncio import AsyncSession
from models.league import League
from schemas.league import LeagueCreate
from sqlalchemy.future import select

async def create_league(db: AsyncSession, league: LeagueCreate):
    
    db_league = League(name=league.name)
    db.add(db_league)
    await db.commit()
    await db.refresh(db_league)
    return db_league

async def get_league_by_id(db:AsyncSession, name: str):
    result=await db.execute(select(League).filter(League.name== name))
    league =result.scalars().first()
    return league

async def get_leagues(db: AsyncSession):
    result = await db.execute(select(League))
    res=result.scalars().all()
    print(res)
    return res
