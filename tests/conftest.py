import json

import pytest
from flask.testing import FlaskClient

from flask_resql.app import create_app


class CustomClient(FlaskClient):
    def __init__(self, *args, **kwargs):
        super(CustomClient, self).__init__(*args, **kwargs)

    def query(self, path, query: str, variables=None):
        res = self.post(path, json={
            "operationName": "q",
            "variables": variables,
            "query": query
        })
        return orjson.loads(res.data)

    def mutation(self, path, mutation: str, variables=None):
        res = self.post(path, json={
            "operationName": "m",
            "variables": variables,
            "query": mutation
        })
        return orjson.loads(res.data)


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


@pytest.fixture
def gql_client(request, app):
    client = app.test_client()

    client.__enter__()
    request.addfinalizer(lambda: client.__exit__(None, None, None))

    return client
