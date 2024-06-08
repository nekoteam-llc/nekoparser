from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from packages.log import hook_fastapi

from .routes.api.v1.connector import router as connector_router
from .routes.api.v1.ping import router as ping_router
from .routes.api.v1.sources import router as sources_router

app = FastAPI()
app.include_router(connector_router)
app.include_router(ping_router)
app.include_router(sources_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

hook_fastapi(app)
