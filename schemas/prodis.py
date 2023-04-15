from pydantic import BaseModel


class ProdiSchema(BaseModel):
    code_prodi: str
    nama_prodi: str

    class Config:
        orm_mode = True


class ProdiGetSchema(ProdiSchema):
    id: str


class ProdiAddSchema(ProdiSchema):
    pass


class ProdiUpdate(ProdiSchema):
    pass
