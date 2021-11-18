import os
from typing import List

import pytest
from fastapi import Depends
from fastapi.testclient import TestClient
from fastapi_jwt_auth import AuthJWT
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse

from app.database.conn import db, Base
from app.database.schema import Users
from app.main import create_app
from app.models import UserToken

"""
1. DB 생성
2. 테이블 생성
3. 테스트 코드 작동
4. 테이블 레코드 삭제 
"""


@pytest.fixture(scope="session")
def app():
    os.environ["API_ENV"] = "test"
    return create_app()


@pytest.fixture(scope="session")
def client(app):
    # Create tables
    Base.metadata.create_all(db.engine)
    return TestClient(app=app)


@pytest.fixture(scope="function", autouse=True)
def session():
    sess = next(db.session())
    yield sess
    clear_all_table_data(
        session=sess,
        metadata=Base.metadata,
        except_tables=[]
    )
    sess.rollback()


@pytest.fixture(scope="function")
def login(session, authorize: AuthJWT = Depends()):
    """
    테스트전 사용자 미리 등록
    :param session:
    :return:
    """
    db_user = Users.create(session=session, email="test@test.com", password="test")
    session.commit()
    access_token = authorize.create_access_token(subject=UserToken.from_orm(db_user).email)
    refresh_token = authorize.create_refresh_token(subject=UserToken.from_orm(db_user).email)
    response = JSONResponse(status_code=200,
                            content=dict(access_token=access_token, refresh_token=refresh_token, msg="OK"))
    authorize.set_access_cookies(access_token, response)
    authorize.set_refresh_cookies(refresh_token, response)
    return response


def clear_all_table_data(session: Session, metadata, except_tables: List[str] = None):
    session.execute("SET FOREIGN_KEY_CHECKS = 0;")
    for table in metadata.sorted_tables:
        if table.name not in except_tables:
            session.execute(table.delete())
    session.execute("SET FOREIGN_KEY_CHECKS = 1;")
    session.commit()
