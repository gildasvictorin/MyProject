from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Path, Request
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from starlette import status
from ..models import Scoperta
from ..database import SessionLocal
from .auth import get_current_user
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates


templates = Jinja2Templates(directory="ScopertaApp/templates")


router = APIRouter(
    prefix="/scoperta",
    tags=["scoperta"]
)






def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]



class ScopertaRequest(BaseModel):
    title: str = Field(min_length=3)
    description: str = Field(min_length=3, max_length=100)
    priority: int = Field(gt=0, lt=6)
    complete: bool



def redirect_to_login():
    redirect_response = RedirectResponse(url="/auth/login-page", status_code=status.HTTP_302_FOUND)
    redirect_response.delete_cookie(key="access_token")
    return redirect_response





###PAGES###

@router.get("/scoperta-page")
async def render_scoperta_page(request: Request, db: db_dependency):
    try:
        user = await get_current_user(request.cookies.get("access_token"))
        if user is None:
            return redirect_to_login()

        scoperta = db.query(Scoperta).filter(Scoperta.owner_id == user.get("id")).all()

        return templates.TemplateResponse(
            request=request,
            name="scoperta.html",
            context={"request": request, "scoperta": scoperta, "user": user}
        )

    except:
        return redirect_to_login()



@router.get("/add-scoperta-page")
async def render_scoperta_page(request: Request):
    try:
        user = await get_current_user(request.cookies.get("access_token"))

        if user is None:
            return redirect_to_login()

        return templates.TemplateResponse(
            request= request,
            name="add-scoperta.html",
            context={"request": request, "user": user}
        )

    except:
        return redirect_to_login()



@router.get("/edit-scoperta-page/{scoperta_id}")
async def render_edit_scoperta_page(request: Request, scoperta_id: int, db: db_dependency):
    try:
        user = await get_current_user(request.cookies.get("access_token"))
        scoperta = db.query(Scoperta).filter(
            Scoperta.id == scoperta_id,
            Scoperta.owner_id == user.get("id")
        ).first()
        if scoperta is None:
            return RedirectResponse(url="/scoperta/scoperta-page", status_code=status.HTTP_303_SEE_OTHER)

        return templates.TemplateResponse(
            request=request,
            name="edit-scoperta.html",
            context={"request": request, "scoperta": scoperta, "user": user})

    except:
        return redirect_to_login()







###ENDPOINTS###
#GET ALL TABLES and User ID

@router.get("/", status_code=status.HTTP_200_OK)
async def read_all(user: user_dependency, db:db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication failed")
    return db.query(Scoperta).filter(Scoperta.owner_id == user.get("id")).all()

#Get ALL ID FROM REQUEST ID AND USERS ID REQUUEST

@router.get("/scoperta/{scoperta_id}", status_code=status.HTTP_200_OK)
async def read_scoperta(user: user_dependency, db: db_dependency, scoperta_id: int= Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication failed")

    scoperta_model = db.query(Scoperta).filter(Scoperta.id == scoperta_id)\
        .filter(Scoperta.owner_id == user.get("id")).first()
    if scoperta_model is not None:
        return scoperta_model
    raise HTTPException(status_code=404, detail="scoperta not found")

#CREATE A POST REQUEST
#ADD NEW CLASS TodoRequest and import from pydantic BaseModel and Field and connect with user

@router.post("/scoperta", status_code=status.HTTP_201_CREATED)
async def create_scoperta(user: user_dependency, db: db_dependency,
                      scoperta_request: ScopertaRequest):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication failed")
    scoperta_model = Scoperta(**scoperta_request.model_dump(), owner_id=user.get("id"))

    db.add(scoperta_model)
    db.commit()



#PUT OR UPDATE ENDPOINT

@router.put("/scoperta/{scoperta_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_scoperta(user: user_dependency, db: db_dependency,
                      scoperta_request: ScopertaRequest,
                      scoperta_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication failed")

    scoperta_model = db.query(Scoperta).filter(Scoperta.id == scoperta_id)\
        .filter(Scoperta.owner_id == user.get("id")).first()
    if scoperta_model is None:
        raise HTTPException(status_code=404, detail="scoperta not found")

    scoperta_model.title = scoperta_request.title
    scoperta_model.description = scoperta_request.description
    scoperta_model.priority = scoperta_request.priority
    scoperta_model.complete = scoperta_request.complete


    db.add(scoperta_model)
    db.commit()


#DELETE ENDPOINT

@router.delete("/scoperta/{scoperta_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_scoperta(user: user_dependency, db: db_dependency, scoperta_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication failed")

    scoperta_model = db.query(Scoperta).filter(Scoperta.id == scoperta_id)\
        .filter(Scoperta.owner_id == user.get("id")).first()
    if scoperta_model is None:
        raise HTTPException(status_code=404, detail="scoperta not found")
    db.query(Scoperta).filter(Scoperta.id == scoperta_id)\
        .filter(Scoperta.owner_id == user.get("id")).delete()

    db.commit()
