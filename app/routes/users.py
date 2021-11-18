from fastapi import APIRouter, Depends
from fastapi_jwt_auth import AuthJWT
from starlette.responses import JSONResponse, Response

from app.database.schema import Users
from app.models import UserMe

router = APIRouter(prefix='/user')


@router.get("/", response_model=UserMe)
async def get_user(authorize: AuthJWT = Depends()):
    """
    get user info
    """
    authorize.jwt_optional()
    current_user = authorize.get_jwt_subject() or None

    if not current_user:
        return JSONResponse(status_code=200)
    user = Users.get(email=current_user)
    if user:
        return user
    return JSONResponse(status_code=400, content=dict(msg="NO_MATCH_USER"))
