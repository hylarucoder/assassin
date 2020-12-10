import datetime
from typing import Optional

from graphql.pyutils import snake_to_camel
from graphql.type.definition import (
    GraphQLField,
    GraphQLObjectType,
)
from graphql.type.schema import GraphQLSchema
from pydantic import constr

from flask_resql import resql as rs
from flask_resql.apps.user.types import TTag, TCategory, TPost
from flask_resql.resql import Validator
from flask_resql.resql.router import GraphRouter

router = GraphRouter()


@router.item("tag", output=TTag)
def get_tag():
    i = 1
    return {"id": 1, "name": f"tag-{i}", "count": i}


@router.list("tags", output=TTag)
def list_tags():
    return [{"id": 1, "name": f"tag-{i}", "count": i} for i in range(2, 10)]


@router.list("categories", output=TCategory)
def list_categories():
    return [{"id": 1, "name": f"category-{i}", "count": i} for i in range(2, 5)]


@router.item("category", output=TCategory)
def list_categories():
    return [{"id": 1, "name": f"category-{i}", "count": i} for i in range(2, 5)]


class ParamsCreateTag(Validator):
    name: constr(min_length=2, max_length=10)


@router.mutation
def create_tag(params: ParamsCreateTag):
    print(params.name)


class ParamsEditTag(Validator):
    id: int
    name: constr(min_length=2, max_length=10)


@router.mutation
def edit_tag(params: ParamsEditTag):
    print(params.id)
    print(params.name)


class ParamsListArchive(Validator):
    q: Optional[constr(min_length=2, max_length=10)]
    date_from: Optional[datetime.date]
    date_to: Optional[datetime.date]
    page: int = 1
    per_page: int = 10
    created_at: Optional[datetime.datetime]
    status: str


@router.pagination("archive", output=TPost)
def list_archive(params: ParamsListArchive):
    date = datetime.date(2020, 12, 1)
    created_at = datetime.datetime(2020, 12, 1)
    return {
        "items": [
            {
                "id": i,
                "name": f"name {i}",
                "content": f"content {i}",
                "date": date,
                "created_at": created_at,
                "category": {"id": i, "status": "DRAFT", "statuses": ["DRAFT"],},
                "keywords": ["k1", "k2"],
                "tags": [
                    {"id": 1, "name": f"tag-{i}", "count": i} for i in range(i, 4)
                ],
            }
            for i in range(params.per_page)
        ],
        "page": params.page,
        "per_page": params.per_page,
        "total": 1,
    }


TViewer = router.build_query("t_viewer")

QueryRootType = GraphQLObjectType(
    name="QueryRoot",
    fields={
        "viewer": GraphQLField(TViewer, resolve=lambda *_: TViewer),
        snake_to_camel("health_check", False): GraphQLField(
            type_=rs.String, resolve=lambda *_: "schema load success"
        ),
    },
)

MutationRootType = router.build_mutation("mutation_root")

Schema = GraphQLSchema(QueryRootType, MutationRootType)
