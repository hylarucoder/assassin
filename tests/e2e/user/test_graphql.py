from tests.utils import CustomClient


def test_health_check(client: CustomClient):
    response = client.query(
        "/graphql",
        query="""
            query q {
              healthCheck
            }
            """,
    )

    assert response.data == {"data": {"healthCheck": "schema load success"}}


def test_post_with_operation_name(client: CustomClient):
    response = client.query(
        "/graphql",
        query="""
query q {
  viewer {
    tags {
      name
      id
    }
    categories {
      name
      id
    }
  	archive(params: {
      q : "1123",
      perPage: 10,
      page: 1,
      status: "1"
    }) {
      items{
        content
        category {
          id
        }
        createdAt
      }
      page
      perPage
    }
  }
}
                """,
    )

    assert response.status == 200
    assert response.data == {
        "data": {
            "viewer": {
                "tags": [
                    {"name": "tag-2", "id": "1"},
                    {"name": "tag-3", "id": "1"},
                    {"name": "tag-4", "id": "1"},
                    {"name": "tag-5", "id": "1"},
                    {"name": "tag-6", "id": "1"},
                    {"name": "tag-7", "id": "1"},
                    {"name": "tag-8", "id": "1"},
                    {"name": "tag-9", "id": "1"},
                ],
                "categories": [
                    {"name": "category-2", "id": "1"},
                    {"name": "category-3", "id": "1"},
                    {"name": "category-4", "id": "1"},
                ],
                "archive": {
                    "items": [
                        {
                            "content": "content 0",
                            "category": None,
                            "createdAt": "2020-12-01 00:00:00",
                        },
                        {
                            "content": "content 1",
                            "category": None,
                            "createdAt": "2020-12-01 00:00:00",
                        },
                        {
                            "content": "content 2",
                            "category": None,
                            "createdAt": "2020-12-01 00:00:00",
                        },
                        {
                            "content": "content 3",
                            "category": None,
                            "createdAt": "2020-12-01 00:00:00",
                        },
                        {
                            "content": "content 4",
                            "category": None,
                            "createdAt": "2020-12-01 00:00:00",
                        },
                        {
                            "content": "content 5",
                            "category": None,
                            "createdAt": "2020-12-01 00:00:00",
                        },
                        {
                            "content": "content 6",
                            "category": None,
                            "createdAt": "2020-12-01 00:00:00",
                        },
                        {
                            "content": "content 7",
                            "category": None,
                            "createdAt": "2020-12-01 00:00:00",
                        },
                        {
                            "content": "content 8",
                            "category": None,
                            "createdAt": "2020-12-01 00:00:00",
                        },
                        {
                            "content": "content 9",
                            "category": None,
                            "createdAt": "2020-12-01 00:00:00",
                        },
                    ],
                    "page": 10,
                    "perPage": 10,
                },
            }
        }
    }
