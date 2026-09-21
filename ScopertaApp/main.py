from fastapi import FastAPI
import models
from ScopertaApp.routers import scoperta
from database import engine

app = FastAPI()


models.Base.metadata.create_all(bind=engine)




@app.get("/healthy")
def health_check():
    return {"status": "healthy"}



app.include_router(scoperta.router)
