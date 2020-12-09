from typing import TypedDict, NamedTuple

import orjson
from flask.testing import FlaskClient


class Response(NamedTuple):
    status: int
    data: dict


class CustomClient(FlaskClient):
    def __init__(self, *args, **kwargs):
        super(CustomClient, self).__init__(*args, **kwargs)

    def query(self, path, query: str, variables=None) -> Response:
        res = self.post(
            path, json={"operationName": "q", "variables": variables, "query": query}
        )
        return Response(status=res.status_code, data=orjson.loads(res.data))

    def mutation(self, path, mutation: str, variables=None) -> Response:
        res = self.post(
            path, json={"operationName": "m", "variables": variables, "query": mutation}
        )
        return Response(status=res.status_code, data=orjson.loads(res.data))
