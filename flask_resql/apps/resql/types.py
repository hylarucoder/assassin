from enum import Enum

from graphql import (
    GraphQLObjectType,
    GraphQLField,
    GraphQLString,
    GraphQLInt,
    GraphQLList,
    GraphQLEnumType,
)


class PostStatus(Enum):
    DRAFT = 4
    PUBLISH = 5
    WITHDRAW = 6

    @property
    def desc(self):
        return "TLDR"


PostStatusEnum = GraphQLEnumType(
    "Episode", PostStatus, description="One of the films in the Star Wars Trilogy"
)

TCategory = GraphQLObjectType(
    "Category",
    fields={
        "id": GraphQLField(GraphQLString),
        "name": GraphQLField(GraphQLString),
        "count": GraphQLField(GraphQLInt),
    },
)

TTag = GraphQLObjectType(
    "Tag",
    fields={
        "id": GraphQLField(GraphQLString),
        "name": GraphQLField(GraphQLString),
        "count": GraphQLField(GraphQLInt),
    },
)

TPost = GraphQLObjectType(
    "Post",
    fields={
        "id": GraphQLField(GraphQLString),
        "name": GraphQLField(GraphQLString),
        "category": GraphQLField(TCategory),
        "tags": GraphQLField(GraphQLList(TTag)),
        "content": GraphQLField(GraphQLString),
        "status": GraphQLField(PostStatusEnum),
        "created_at": GraphQLField(GraphQLInt),
        "updated_at": GraphQLField(GraphQLInt),
    },
)
