from app.database.schema import Users


def test_registration(client, session):
    """
    레버 로그인
    :param client:
    :param session:
    :return:
    """
    user = dict(email="test@test.com", password="test", name="test", phone_number="01099999999")
    res = client.post("api/auth/register/email", json=user)
    cookies = res.cookies
    assert res.status_code == 201
    assert "access_token_cookie" in cookies.keys()


def test_registration_exist_email(client, session):
    """
    레버 로그인
    :param client:
    :param session:
    :return:
    """
    user = dict(email="test@test.com", password="test", name="test", phone_number="01099999999")
    db_user = Users.create(session=session, **user)
    session.commit()
    res = client.post("api/auth/register/email", json=user)
    res_body = res.json()
    assert res.status_code == 400
    assert 'EMAIL_EXISTS' == res_body["msg"]
