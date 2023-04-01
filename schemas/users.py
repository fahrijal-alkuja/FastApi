from pydantic import BaseModel


class UserSchema(BaseModel):
    id: int
    name: str
    email: str
    rule: str

    class Config:
        orm_mode = True


class UserAddSChema(UserSchema):
    password: str
