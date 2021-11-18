from dataclasses import asdict

import uvicorn
from fastapi import FastAPI, Request, Depends
from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth.exceptions import AuthJWTException
from fastapi.security import APIKeyHeader, APIKeyCookie
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse

from app.common.config import JWTConfig, conf
from app.database.conn import db
from app.middlewares.trusted_hosts import TrustedHostMiddleware
from app.routes import index, auth, users
from app.middlewares.token_validator import access_control


def create_app():
    """
    앱 함수 실행
    :return: app : FastAPI instance
    """
    # Config
    c = conf()
    conf_dict = asdict(c)
    # APP
    app = FastAPI()
    # DB
    db.init_app(app, **conf_dict)

    # Redis

    # AuthJWT
    @AuthJWT.load_config
    def get_config():
        return JWTConfig()

    @app.exception_handler(AuthJWTException)
    def authjwt_exception_handler(request: Request, exc: AuthJWTException):
        return JSONResponse(status_code=exc.status_code, content=dict(detail=exc.message))

    # Middleware
    # app.add_middleware(middleware_class=BaseHTTPMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=conf().ALLOW_SITE,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=conf().TRUSTED_HOSTS, except_path=["/health"])

    # Router
    app.include_router(index.router)
    app.include_router(auth.router, tags=["Authentication"], prefix="/api")
    app.include_router(users.router, tags=["Users"], prefix="/api")

    return app


app = create_app()

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
