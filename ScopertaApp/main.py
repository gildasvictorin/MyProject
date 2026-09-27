from fastapi import FastAPI, Request, status
from . import models
from ScopertaApp.routers import scoperta, auth, users, admin
from .database import engine
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse





app = FastAPI()


models.Base.metadata.create_all(bind=engine)


app.mount("/static", StaticFiles(directory="ScopertaApp/static"), name="static")






@app.get("/")
def test(request: Request):
    return RedirectResponse(url="/scoperta/scoperta-page", status_code=status.HTTP_302_FOUND)


@app.get("/healthy")
def health_check():
    return {"status": "healthy"}



app.include_router(scoperta.router)
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(admin.router)
