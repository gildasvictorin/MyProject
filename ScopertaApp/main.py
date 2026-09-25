from fastapi import FastAPI, Request
from . import models
from ScopertaApp.routers import scoperta, auth, users, admin
from .database import engine
from fastapi.templating import Jinja2Templates





app = FastAPI()


models.Base.metadata.create_all(bind=engine)


templates=Jinja2Templates(directory="ScopertaApp/templates")



@app.get("/")
def test(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="home.html",
        context={"request": request}
    )


@app.get("/healthy")
def health_check():
    return {"status": "healthy"}



app.include_router(scoperta.router)
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(admin.router)
