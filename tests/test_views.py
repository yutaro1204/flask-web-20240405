from flask import session
from .. import db
import bcrypt
from ..models import User

# サインアップテスト
def test_sign_up_get(client):
    with client:
        response = client.get('/sign_up')
        assert response.status_code == 200

def test_sign_up_post(client):
    name = "test"
    email = "test@gmail.com"
    password = "hogehoge"

    with client:
        response = client.post('/sign_up', data={
            "name": name,
            "email": email,
            "password": password
        })
        assert response.status_code == 302
        assert session.get('email') == email
        user = db.session.execute(db.select(User).filter_by(email=email)).scalar_one_or_none()
        assert user.name == name
        assert user.email == email
        assert bcrypt.checkpw(password.encode('utf8'), user.password.encode('utf8'))

def test_sign_up_user_already_exists(app, client):
    name = "test"
    email = "test@gmail.com"
    password = "hogehoge"

    with app.app_context():
        salt = bcrypt.gensalt(rounds=12, prefix=b'2b')
        hashpw = bcrypt.hashpw(password.encode('utf8'), salt)
        user = User(name=name, email=email, password=hashpw.decode('utf8'))
        db.session.add(user)
        db.session.commit()

    with client:
        response = client.post('/sign_up', data={
            "name": name,
            "email": email,
            "password": password
        })
        assert response.status_code == 200
        assert session.get('email') is None

# サインインテスト
def test_sign_in_get(client):
    with client:
        response = client.get('/sign_in')
        assert response.status_code == 200

def test_sign_in_post(app, client):
    email = "test@gmail.com"
    password = "hogehoge"

    with app.app_context():
        salt = bcrypt.gensalt(rounds=12, prefix=b'2b')
        hashpw = bcrypt.hashpw(password.encode('utf8'), salt)
        user = User(name="test", email=email, password=hashpw.decode('utf8'))
        db.session.add(user)
        db.session.commit()

    with client:
        response = client.post('/sign_in', data={
            "email": email,
            "password": password
        })
        assert response.status_code == 302
        assert session.get('email') == email

def test_sign_in_user_already_signed_in(client):
    email = "test@gmail.com"
    password = "hogehoge"

    with client.session_transaction() as session:
        session['email'] = email

    with client:
        response = client.post('/sign_in', data={
            "email": email,
            "password": password
        })
        assert response.status_code == 302

def test_sign_in_given_password_is_wrong(app, client):
    email = "test@gmail.com"
    password = "hogehoge"

    with app.app_context():
        salt = bcrypt.gensalt(rounds=12, prefix=b'2b')
        hashpw = bcrypt.hashpw(password.encode('utf8'), salt)
        user = User(name="test", email=email, password=hashpw.decode('utf8'))
        db.session.add(user)
        db.session.commit()

    with client:
        response = client.post('/sign_in', data={
            "email": email,
            "password": "foofoo"
        })
        assert response.status_code == 200
        assert session.get('email') is None

def test_sign_in_user_does_not_exist(app, client):
    email = "test@gmail.com"
    password = "hogehoge"

    with client:
        response = client.post('/sign_in', data={
            "email": email,
            "password": password
        })
        assert response.status_code == 200
        assert session.get('email') is None

# サインアウトテスト　
def test_sign_out_post(client):
    email = "test@gmail.com"

    with client.session_transaction() as session:
      session['email'] = email

    response = client.post('/sign_out')
    assert response.status_code == 302
