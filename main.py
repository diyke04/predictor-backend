from typing import List
import fastapi as _fastapi
import schema as _schema
import sqlalchemy.orm as _orm
import services as _services
import uvicorn

from fastapi.middleware.cors import CORSMiddleware

app=_fastapi.FastAPI()

origins =[
" http://localhost:3000",
]

app.add_middleware(CORSMiddleware,allow_origins=origins,)


@app.get('/matches',response_model=List[_schema.Match])
async def get_all_matches(db:_orm.Session=_fastapi.Depends(_services.get_db)):
    return await _services.get_all_matches(db)

@app.get('/match',response_model=_schema.Match)
async def get_matchs(id,db:_orm.Session=_fastapi.Depends(_services.get_db)):
    return await _services.get_match(id=id,db=db)

@app.post('/create-match')
async def create_match(match: _schema.MatcheCreate,db:_orm.Session=_fastapi.Depends(_services.get_db)):
    return await _services.create_match(match=match,db=db)

@app.put('/update-match-result')
async def update_match_result(data:_schema.Match,db:_orm.Session=_fastapi.Depends(_services.get_db)):
    return await _services.update_match_result(data=data,db=db)

@app.put('/update-match-prediction')
async def update_match_prediction(data:_schema.Match,db:_orm.Session=_fastapi.Depends(_services.get_db)):
    return await _services.update_match_prediction(data=data,db=db)






if __name__ == '__main__':

    uvicorn.run(app, host='127.0.0.1', port=8000)

