import datetime
from enum import Enum
from typing import List

from pydantic import Field

from flask_resql.resql import Serializer
from flask_resql.resql.utils import transform_serializer_field


def object_type(cls):
    schema = cls.schema()
    obj_type = transform_serializer_field(
        f"/{cls.__name__}",
        cls.__name__,
        schema,
        parent_schema=None,
        global_schema=schema,
    )
    obj_type.__serializer__ = cls
    return obj_type


class CategoryStatusEnum(str, Enum):
    """
    Category Status 枚举值
    """

    DRAFT = "DRAFT"
    PUBLISH = "PUBLISH"
    WITHDRAW = "WITHDRAW"

    @property
    def desc(self):
        return "TLDR"


@object_type
class TCategory(Serializer):
    """
    分类
    """

    id: str
    name: str
    count: int
    status: CategoryStatusEnum
    statuses: List[CategoryStatusEnum]


@object_type
class TTag(Serializer):
    """
    标签
    """

    id: str
    name: str
    count: int


class PostStatusEnum(str, Enum):
    """
    Post Status 枚举值
    """

    DRAFT = "DRAFT"
    PUBLISH = "PUBLISH"
    WITHDRAW = "WITHDRAW"

    @property
    def desc(self):
        return "TLDR"


@object_type
class TPost(Serializer):
    """
    文章
    """

    id: str
    name: str
    # TODO: 考虑一下是不是应该把 __serializer__ 去掉
    category: TCategory.__serializer__
    tags: List[TTag.__serializer__] = Field(description="简单的描述 Tags")
    content: str
    status: PostStatusEnum
    date: datetime.date
    created_at: datetime.datetime
    updated_at: datetime.datetime
    keywords: List[str] = Field(description="简单的描述 keywords")
