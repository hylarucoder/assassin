import datetime
from enum import Enum

from graphql import GraphQLEnumType
from pydantic.main import BaseModel

from flask_resql.resql import Serializer
from flask_resql.resql.utils import transform_serializer_model


def object_type(cls):
    schema = cls.schema()
    obj_type = transform_serializer_model("/", cls.__name__, schema)
    obj_type.__serializer__ = cls
    return obj_type


class CategoryStatusEnum(str, Enum):
    DRAFT = "DRAFT"
    PUBLISH = "PUBLISH"
    WITHDRAW = "WITHDRAW"

    @property
    def desc(self):
        return "TLDR"


# EnumCategoryStatus = GraphQLEnumType(
#     "EnumCategoryStatus", CategoryStatusEnum, description="One of the films in the Star Wars Trilogy"
# )


@object_type
class TCategory(Serializer):
    id: str
    name: str
    count: int
    status: CategoryStatusEnum


@object_type
class TTag(Serializer):
    id: str
    name: str
    count: int


@object_type
class TPost(BaseModel):
    id: str
    name: str
    category: TCategory.__serializer__
    # tags: List[TagSerializer]
    content: str
    status: str
    date: datetime.date
    created_at: datetime.datetime
    updated_at: datetime.datetime
