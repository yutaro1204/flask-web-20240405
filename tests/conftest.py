import pytest
from .. import create_app, db

@pytest.fixture()
def app():
    app = create_app()

    # set up
    with app.app_context():
        db.create_all()

    yield app

    # tear down
    with app.app_context():
        db.drop_all()

@pytest.fixture()
def client(app):
    return app.test_client()

@pytest.fixture()
def runner(app):
    return app.test_cli_runner()
