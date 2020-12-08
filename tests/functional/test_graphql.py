def test_post_with_operation_name(client):
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
      per_page: 10,
      page: 1,
      status: "1"
      
      
    }) {
      items{
        content
        category {
          id
        }
        tags {
          id
        }
        created_at
      }
      page
      per_page
    }
  }
}
                """
    )

    print(response.data)
    assert response.status_code == 200
    assert response.data == {
        "data": {
            "test": "Hello World",
            "shared": "Hello Everyone"
        }
    }
