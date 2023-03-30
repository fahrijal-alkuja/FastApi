
from fastapi import FastAPI
from routers.users import user
from routers.login import login

from config.openapi import tags_metadata

app = FastAPI(
    title="EWS API",
    description="REST API using python and mysql",
    version="0.0.1",
    openapi_tags=tags_metadata,
)

app.include_router(user)
app.include_router(login)
