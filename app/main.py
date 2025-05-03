from fastapi import FastAPI
from app.api.routes import router
app = FastAPI(title="RV-CLI API"); app.include_router(router) 