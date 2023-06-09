
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers.users import user
from routers.login import login
from routers.prodi import prodi
from routers.aktivitas_mhs import Aktivitas
from routers.problem import problem

from config.openapi import tags_metadata

app = FastAPI(
    title="EWS API",
    description="REST API using python and mysql",
    version="0.0.1",
    openapi_tags=tags_metadata,
)

origins = [
    "http://127.0.0.1:8000/",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user)
app.include_router(login)
app.include_router(prodi)
app.include_router(Aktivitas)
app.include_router(problem)
