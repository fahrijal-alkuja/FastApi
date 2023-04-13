from pydantic import BaseModel


class Prodi(BaseModel):
    id: int
    nama_prodi: str
    code_prodi: str

    class Config:
        orm_mode = True


class UserSchema(BaseModel):
    name: str
    email: str
    rule: str
    prodi_id: str

    class Config:
        orm_mode = True


class UserAddSChema(UserSchema):
    password: str


class UserGetSchema(UserSchema):
    id: int
    prodi: Prodi


class UserUpdate(UserSchema):
    id: int
