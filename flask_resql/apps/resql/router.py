import inspect
import typing
from typing import Callable, Any, Dict

from graphql import (
    GraphQLField,
    GraphQLList,
)

import flask_resql.apps.resql as rs
from flask_resql.apps.resql.utils import gen_args_from_params, create_field


def get_typed_signature(call: Callable) -> inspect.Signature:
    signature = inspect.signature(call)
    global_ns = getattr(call, "__globals__", {})
    typed_params = [
        inspect.Parameter(
            name=param.name,
            kind=param.kind,
            default=param.default,
            annotation=get_typed_annotation(param, global_ns),
        )
        for param in signature.parameters.values()
    ]
    typed_signature = inspect.Signature(typed_params)
    return typed_signature


def get_typed_annotation(param: inspect.Parameter, global_ns: Dict[str, Any]) -> Any:
    annotation = param.annotation
    return annotation


class ResolverResult(typing.NamedTuple):
    name: str
    resolver: typing.Callable
    parameters: typing.Mapping[str, inspect.Parameter]
    has_root: bool
    has_info: bool

    def get_item_args(self):
        kwargs = {}
        has_id = self.parameters.get("id", False)
        if has_id:
            id_type = self.parameters["id"].annotation
            if id_type is inspect.Signature.empty:
                id_type = rs.ID
            kwargs["id"] = id_type(required=True)
        self.append_params_if_possible(kwargs)
        return kwargs

    def get_list_args(self):
        kwargs = {}
        self.append_params_if_possible(kwargs)
        return kwargs

    def get_pagination_args(self):
        return self.get_list_args()

    def get_mutation_args(self):
        return self.get_list_args()

    def append_params_if_possible(self, kwargs):
        has_params = self.parameters.get("params", False)
        if has_params:
            params_type = self.parameters["params"].annotation
            kwargs["params"] = gen_args_from_params(self.name, params_type)


def parse_resolver(resolver_function, name):
    resolver_function_sig = get_typed_signature(resolver_function)

    has_root = resolver_function_sig.parameters.get("root", False)
    has_info = resolver_function_sig.parameters.get("info", False)
    has_params = resolver_function_sig.parameters.get("params", False)
    has_id = resolver_function_sig.parameters.get("id", False)

    def combine_resolver(root, info, *args, **kwargs):
        extra_kwargs = {}
        if has_info:
            extra_kwargs["info"] = info
        if has_root:
            extra_kwargs["root"] = root
        if has_params:
            extra_kwargs["params"] = has_params.annotation(**kwargs.pop("params"))
        if has_id:
            extra_kwargs["id"] = root

        return resolver_function(*args, **kwargs, **extra_kwargs)

    return ResolverResult(
        name=name,
        resolver=combine_resolver,
        parameters=resolver_function_sig.parameters,
        has_root=has_root,
        has_info=has_info,
        # has_params=has_params,
        # has_id=has_id,
    )


class GraphRouter:
    query_fields: Dict[str, Any]
    mutation_fields: Dict[str, Any]

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
                        "page": create_field('page', rs.Int),
                        "perPage": create_field('per_page', rs.Int),
                        "hasNextPage": create_field("per_page", rs.Int),
                        "items": create_field("items", GraphQLList(output)),
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
