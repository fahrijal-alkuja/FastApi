from pydantic import BaseModel, validator, EmailStr


class Prodi(BaseModel):
    id: int
    nama_prodi: str
    code_prodi: str

    class Config:
        orm_mode = True


class UserSchema(BaseModel):
    name: str
    email: EmailStr
    rule: str
    prodi_id: str

    class Config:
        orm_mode = True


# Fungsi validasi untuk memastikan nama, email, rule, dan prodi_id tidak kosong

    @validator('name', 'email', 'rule', 'prodi_id')
    def check_not_empty(cls, value):
        if not value:
            raise ValueError('Field must not be empty')
        return value

    # Fungsi validasi untuk memastikan email dalam format yang valid
    @validator('email')
    def validate_email(cls, email):
        if not EmailStr.validate(email):
            raise ValueError('Invalid email format')
        return email


class UserAddSChema(UserSchema):
    password: str

    @validator('password')
    def validate_password(cls, password):
        if len(password) < 8:
            raise ValueError('Password must have at least 8 characters')
        return password


class UserGetSchema(UserSchema):
    id: int
    prodi: Prodi


class UserUpdate(UserSchema):
    id: int
