from pydantic import BaseModel


class UserSchema(BaseModel):
    name: str
    email: str
    rule: str

    class Config:
        orm_mode = True


class UserAddSChema(UserSchema):
    password: str


class UserGetSchema(UserSchema):
    id: int


class UserUpdate(UserSchema):
    id: int
