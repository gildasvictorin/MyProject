from fastapi import FastAPI
from . import models
from ScopertaApp.routers import scoperta, auth, users, admin
from .database import engine

app = FastAPI()


models.Base.metadata.create_all(bind=engine)




@app.get("/healthy")
def health_check():
    return {"status": "healthy"}



app.include_router(scoperta.router)
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(admin.router)
