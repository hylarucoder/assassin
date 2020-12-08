def test_home(client):
    rv = client.post("/test", json={"a": 12})
    assert rv.is_json
    assert rv.json["a"] == 12


def test_home_bad(client):
    rv = client.post("/test", json={"a": "str"})
    assert rv.is_json
    assert rv.status_code == 400
