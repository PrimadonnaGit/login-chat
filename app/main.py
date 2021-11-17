from dataclasses import asdict

import uvicorn
from fastapi import FastAPI, Request
from fastapi_jwt_auth.exceptions import AuthJWTException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse

from app.common.config import conf
from app.database.conn import db
from app.middlewares.trusted_hosts import TrustedHostMiddleware
from app.routes import index, auth
from middlewares.token_validator import access_control


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

    # Middleware
    app.add_middleware(middleware_class=BaseHTTPMiddleware, dispatch=access_control)
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

    # Exception

    @app.exception_handler(AuthJWTException)
    def authjwt_exception_handler(request: Request, exc: AuthJWTException):
        return JSONResponse(status_code=exc.status_code, content=dict(detail=exc.message))

    return app


app = create_app()

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
