from fastapi import FastAPI

from app.api.routes import router
from app.db.init_db import init_db

init_db()
app = FastAPI(title="Credit Risk Early Warning System", version="0.1.0")
app.include_router(router)
