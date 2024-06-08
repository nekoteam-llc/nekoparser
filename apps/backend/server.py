from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from packages.log import hook_fastapi

from .routes.api.v1.ping import router as ping_router

app = FastAPI()
app.include_router(ping_router)


origins = ["http://localhost"]

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"http://localhost:\d+",
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

hook_fastapi(app)
