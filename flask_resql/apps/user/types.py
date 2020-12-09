import datetime
from enum import Enum
from typing import List

from graphql import (
    GraphQLField,
    GraphQLString,
    GraphQLInt,
    GraphQLEnumType,
)
from pydantic.main import BaseModel

from flask_resql.apps.resql import ObjectType
from flask_resql.apps.resql.serializer import Serializer
from flask_resql.apps.resql.utils import transform_serializer_model


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


class CategorySerializer(Serializer):
    id: str
    name: str
    count: int


TCategory = ObjectType(
    "Category",
    fields={
        "id": GraphQLField(GraphQLString),
        "name": GraphQLField(GraphQLString),
        "count": GraphQLField(GraphQLInt),
    },
)


class TagSerializer(Serializer):
    id: str
    name: str
    count: int


TTag = ObjectType(
    "Tag",
    fields={
        "id": GraphQLField(GraphQLString),
        "name": GraphQLField(GraphQLString),
        "count": GraphQLField(GraphQLInt),
    },
)


class TPostModel(BaseModel):
    id: str
    name: str
    category: CategorySerializer
    # tags: List[TagSerializer]
    content: str
    status: str
    date: datetime.date
    created_at: datetime.datetime
    updated_at: datetime.datetime

    @classmethod
    def build_type(cls):
        schema = cls.schema()
        return transform_serializer_model("TPost", schema)


TPost = TPostModel.build_type()
