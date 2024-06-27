from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.endpoints import auth, fixtures, predictions,league


origins =['http://localhost:5173','https://predictor-backend-one.vercel.app']

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(fixtures.router, prefix="/api/fixtures", tags=["fixtures"])
app.include_router(predictions.router, prefix="/api/predictions", tags=["predictions"])
app.include_router(league.router, prefix="/api/leagues", tags=["leagues"])


