from typing import Dict

from graphql import (
    GraphQLField,
    GraphQLList,
)

import flask_resql.resql as rs
from flask_resql.resql import create_scalar_field
from flask_resql.resql.inspect import parse_resolver


class GraphRouter:
    query_fields: Dict[str, GraphQLField]
    mutation_fields: Dict[str, GraphQLField]

    def __init__(self):
        self.query_fields = {}
        self.mutation_fields = {}

    def item(self, name, output):
        def decorate(resolver_function):
            resolver_result = parse_resolver(resolver_function, name)
            field = GraphQLField(
                output,
                args=resolver_result.get_item_args(),
                resolve=resolver_result.resolver,
                description=resolver_function.__doc__ or "",
            )
            self.query_fields[f"{name}"] = field
            return field

        return decorate

    def list(self, name, output):
        def decorate(resolver_function):
            resolver_result = parse_resolver(resolver_function, name)
            field = GraphQLField(
                GraphQLList(output),
                args=resolver_result.get_list_args(),
                resolve=resolver_result.resolver,
                description=resolver_function.__doc__ or "nops",
            )
            self.query_fields[f"{name}"] = field
            return field

        return decorate

    def pagination(self, name, output):
        def decorate(resolver_function):
            resolver_result = parse_resolver(resolver_function, name)
            field = GraphQLField(
                rs.ObjectType(
                    f"pagination_{name}",
                    fields={
                        "page": create_scalar_field("page", rs.Int),
                        "per_page": create_scalar_field("per_page", rs.Int),
                        "has_next_page": create_scalar_field("per_page", rs.Int),
                        "items": create_scalar_field("items", output, use_list=True),
                    },
                ),
                args=resolver_result.get_pagination_args(),
                resolve=resolver_result.resolver,
                description=resolver_function.__doc__ or "nops",
            )
            self.query_fields[name] = field
            return field

        return decorate

    def mutation(self, name_or_fn, output=None):
        def decorate(resolver_function, name):
            resolver_result = parse_resolver(resolver_function, name)
            field = GraphQLField(
                output or rs.Boolean,
                args=resolver_result.get_mutation_args(),
                resolve=resolver_result.resolver,
                description=resolver_function.__doc__ or "nops",
            )
            self.mutation_fields[f"{name}"] = field
            return field

        if callable(name_or_fn):
            return decorate(name_or_fn, name_or_fn.__name__)
        return lambda fn: decorate(fn, name_or_fn)

    def build_query(self, type_name):
        return rs.ObjectType(
            name=type_name,
            fields={name: field for name, field in self.query_fields.items()},
        )

    def build_mutation(self, type_name):
        return rs.ObjectType(
            name=type_name,
            fields={name: field for name, field in self.mutation_fields.items()},
        )
