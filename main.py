from fastapi import FastAPI

from api.endpoints import auth, fixtures, predictions,league
from db.base import Base
from db.session import engine


app = FastAPI()

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(fixtures.router, prefix="/fixtures", tags=["fixtures"])
app.include_router(predictions.router, prefix="/predictions", tags=["predictions"])
app.include_router(league.router, prefix="/leagues", tags=["leagues"])

# Run the application
# uvicorn main:app --reload
