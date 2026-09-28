import sys

from starlette.templating import Jinja2Templates

from .. import models

sys.path.append("..")
from starlette.responses import RedirectResponse
from pathlib import Path
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Form, Request
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from starlette import status
from .auth import get_current_user
from fastapi.responses import HTMLResponse
from ..models import Scoperta, Users
from ..database import SessionLocal, engine
from passlib.context import CryptContext







router = APIRouter(
    prefix="/user",
    tags=["user"],
    responses={404: {"description": "Not Found"}}
)


models.Base.metadata.create_all(bind=engine)
templates = Jinja2Templates(
    directory=str(Path(__file__).resolve().parent.parent / "templates")
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]
bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")



class UserVerification(BaseModel):
    username: str
    password: str
    new_password: str = Field(min_length=6)


###PAGES TO EDIT USER PASSWORD###

@router.get("/edit-password", response_class=HTMLResponse)
async def edit_user_view(request: Request):
    user = await get_current_user(request.cookies.get("access_token"))
    if user is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)

    return templates.TemplateResponse(
        request=request,
        name="edit-user-password.html",
        context={"request": request, "user": user}
    )



##display correct message when to edit the password


@router.post("/edit-password", response_class=HTMLResponse)
async def user_password_change(request: Request, username: str = Form(...),
                               password: str = Form(...), password2: str = Form(...),
                               db: Session = Depends(get_db)):
    token = request.cookies.get("access_token")
    if not token:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)
    try:
        user = await get_current_user(token)
    except HTTPException:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)
    if user is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)

    user_data = db.query(models.Users).filter(models.Users.id == user.get("id")).first()

    msg = "Invalid username or password"

    if user_data is not None:
        if username == user_data.username and bcrypt_context.verify(password, user_data.hashed_password):
            user_data.hashed_password = bcrypt_context.hash(password2)
            db.add(user_data)
            db.commit()
            msg = 'Password updated'

    return templates.TemplateResponse(
        request=request,
        name="edit-user-password.html",
        context={"request": request, "user": user, "msg": msg}
    )



###ENDPOINT FOR MY BACKEND###


@router.get("/", status_code=status.HTTP_200_OK)
async def get_user(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication failed")
    return db.query(Users).filter(Users.id == user.get("id")).first()



@router.put("/password", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(user: user_dependency, db: db_dependency, user_verification: UserVerification):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication failed")
    user_model = db.query(Users).filter(Users.id == user.get("id")).first()

    if not bcrypt_context.verify(user_verification.password, user_model.hashed_password):
        raise HTTPException(status_code=401, detail="Error on password change")
    user_model.hashed_password = bcrypt_context.hash(user_verification.new_password)
    db.add(user_model)
    db.commit()



@router.put("/phonenumber/{phone_number}", status_code=status.HTTP_204_NO_CONTENT)
async def change_phone_number(user: user_dependency, db: db_dependency, phone_number: str):

    if user is None:
        raise HTTPException(status_code=401, detail="Authentication failed")
    user_model = db.query(Users).filter(Users.id == user.get("id")).first()
    user_model.phone_number = phone_number
    db.add(user_model)
    db.commit()
