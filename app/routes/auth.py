import bcrypt
from fastapi import APIRouter, Depends
from fastapi_jwt_auth import AuthJWT
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse

from app.database.conn import db
from app.database.schema import Users
from app.models import SnsType, Token, UserMe, UserToken, UserRegister

"""
1. 구글 로그인을 위한 구글 앱 준비 (구글 개발자 도구)
2. FB 로그인을 위한 FB 앱 준비 (FB 개발자 도구)
3. 카카오 로그인을 위한 카카오 앱준비( 카카오 개발자 도구)
4. 이메일, 비밀번호로 가입 (v)
5. 가입된 이메일, 비밀번호로 로그인, (v)
6. JWT 발급 (v)
7. 이메일 인증 실패시 이메일 변경
8. 이메일 인증 메일 발송
9. 각 SNS 에서 Unlink
10. 회원 탈퇴
11. 탈퇴 회원 정보 저장 기간 동안 보유(법적 최대 한도 내에서, 가입 때 약관 동의 받아야 함, 재가입 방지 용도로 사용하면 가능)
400 Bad Request
401 Unauthorized
403 Forbidden
404 Not Found
405 Method not allowed
500 Internal Error
502 Bad Gateway
504 Timeout
200 OK
201 Created
"""

router = APIRouter(prefix="/auth")


@router.post("/login/{sns_type}", status_code=200, response_model=Token)
async def login(sns_type: SnsType, user_info: UserRegister, authorize: AuthJWT = Depends()):
    """
    With authjwt_cookie_csrf_protect set to True, set_access_cookies() and
    set_refresh_cookies() will now also set the non-httponly CSRF cookies
    """
    if sns_type == SnsType.email:
        is_exist = await is_email_exist(user_info.email)
        if not user_info.email or not user_info.password:
            return JSONResponse(status_code=400, content=dict(msg="Email and password must be provided'"))
        if not is_exist:
            return JSONResponse(status_code=400, content=dict(msg="NO_MATCH_USER"))
        user = Users.get(email=user_info.email)
        is_verified = bcrypt.checkpw(user_info.password.encode("utf-8"), user.password.encode("utf-8"))
        if not is_verified:
            return JSONResponse(status_code=400, content=dict(msg="NO_MATCH_USER"))

        # Create the tokens and passing to set_access_cookies or set_refresh_cookies
        access_token = authorize.create_access_token(subject=user_info.email)
        refresh_token = authorize.create_refresh_token(subject=user_info.email)
        # Set the JWT and CSRF double submit cookies in the response
        response = JSONResponse(status_code=200,
                                content=dict(access_token=access_token, refresh_token=refresh_token, msg="OK"))
        authorize.set_access_cookies(access_token, response)
        authorize.set_refresh_cookies(refresh_token, response)
        return response
    return JSONResponse(status_code=400, content=dict(msg="NOT_SUPPORTED"))


@router.post("/refresh")
async def refresh(authorize: AuthJWT = Depends()):
    authorize.jwt_refresh_token_required()

    current_user = authorize.get_jwt_subject()
    new_access_token = authorize.create_access_token(subject=current_user)
    # Set the JWT and CSRF double submit cookies in the response
    response = JSONResponse(status_code=200, content=dict(msg="REFRESH"))
    authorize.set_access_cookies(new_access_token, response)
    return response


@router.delete('/logout')
def logout(authorize: AuthJWT = Depends()):
    """
    Because the JWT are stored in an httponly cookie now, we cannot
    log the user out by simply deleting the cookie in the frontend.
    We need the backend to send us a response to delete the cookies.
    """
    authorize.jwt_required()
    response = JSONResponse(status_code=200, content=dict(msg="LOGOUT"))
    authorize.unset_jwt_cookies(response)
    return response


@router.post("/register/{sns_type}", status_code=201, response_model=Token)
async def register(sns_type: SnsType, reg_info: UserRegister, session: Session = Depends(db.session),
                   authorize: AuthJWT = Depends()):
    """
    `회원가입 API`\n
    :param authorize:
    :param sns_type:
    :param reg_info:
    :param session:
    :return:
    """
    if sns_type == SnsType.email:
        is_exist = await is_email_exist(reg_info.email)
        if not reg_info.email or not reg_info.password:
            return JSONResponse(status_code=400, content=dict(msg="Email and password must be provided"))
        if is_exist:
            return JSONResponse(status_code=400, content=dict(msg="EMAIL_EXISTS"))
        hash_password = bcrypt.hashpw(reg_info.password.encode("utf-8"), bcrypt.gensalt())
        new_user = Users.create(session, auto_commit=True, password=hash_password, email=reg_info.email)
        access_token = authorize.create_access_token(subject=UserToken.from_orm(new_user).email)
        refresh_token = authorize.create_refresh_token(subject=UserToken.from_orm(new_user).email)
        response = JSONResponse(status_code=201,
                                content=dict(access_token=access_token, refresh_token=refresh_token, msg="OK"))
        authorize.set_access_cookies(access_token, response)
        authorize.set_refresh_cookies(refresh_token, response)
        return response

    return JSONResponse(status_code=400, content=dict("NOT_SUPPORTED"))


async def is_email_exist(email: str):
    get_email = Users.get(email=email)
    if get_email:
        return True
    return False
