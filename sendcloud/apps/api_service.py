""" The main app module """
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from sendcloud.routers import all_routers
from sendcloud.utils import settings

print(settings.database_url)
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

for router in all_routers:
    app.include_router(router)
