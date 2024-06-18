from pydantic import BaseModel

class UserCreate(BaseModel):
    username: str
    password: str
    email: str

class UserUpdateRole(BaseModel):
    is_admin: bool | None = None

class LoginUser(BaseModel):
    username:str
    password:str

class User(BaseModel):
    id: int
    username: str
    email: str
    is_admin: bool | None = None
    token:int
    
    class Config:
        from_attributes = True
