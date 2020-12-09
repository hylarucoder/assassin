# flask-resql

RESTful Experience with GraphQL API

## Features

1. use graphql in your familiar RESTful way
    - easy strict validating with pydantic
    - easy relaxing serialize data
    - organize your view layer code just like bp.get bp.post
2. jwt auth with different audience
3. SQLAlchemy integrated
4. poetry for project builder

## TODO List

- [ ] Better Validation Experience
- [ ] More Field Support
    - [X] EnumField
    - [X] List Scalar
    - [ ] List Field/Enum
    - [ ] JSONField/AutoCamelJsonField
    - [ ] Union Field
    - [ ] Self Reference Field
    - [ ] Limit Bi-Direction Fields
- [ ] Hashed Name - No More Field Naming Collision, Maybe
- [ ] More Unit Test
