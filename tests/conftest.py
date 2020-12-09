import pytest

from flask_resql.app import create_app

from tests.utils import CustomClient


@pytest.fixture
def app():
    config = {
        "TESTING": True,
    }

    app = create_app(config=config)
    app.test_client_class = CustomClient

    with app.app_context():
        # init_db(app)
        yield app


@pytest.fixture
def client(request, app):
    client = app.test_client()

    client.__enter__()
    request.addfinalizer(lambda: client.__exit__(None, None, None))

    return client
