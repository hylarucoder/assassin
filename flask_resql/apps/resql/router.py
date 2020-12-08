import inspect
import typing
from typing import Callable, Any, Dict

from graphql import (
    GraphQLField,
    GraphQLList,
    GraphQLObjectType,
    GraphQLArgument,
    GraphQLNonNull,
    GraphQLInputObjectType,
    GraphQLInputField,
)

import flask_resql.apps.resql as rs


def get_input_field(type_, required=False) -> GraphQLInputField:
    if not required:
        return GraphQLInputField(type_)
    else:
        return GraphQLInputField(GraphQLNonNull(type_))


def gen_field(k, v, schema):
    """
    # TODO: nested support
    """
    required = k in schema.get("required", [])
    if v["type"] == "string":
        if v.get("format", None) == "date":
            return get_input_field(rs.Date, required)
        if v.get("format", None) == "date-time":
            return get_input_field(rs.DateTime, required)
        return get_input_field(rs.String, required)
    if v["type"] == "integer":
        return GraphQLInputField(rs.Int)
    raise NotImplementedError


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

    def get_item_kwargs(self):
        kwargs = {}
        has_id = self.parameters.get("id", False)
        if has_id:
            id_type = self.parameters["id"].annotation
            if id_type is inspect.Signature.empty:
                id_type = rs.ID
            kwargs["id"] = id_type(required=True)
        self.append_params_if_possible(kwargs)
        return kwargs

    def get_list_kwargs(self):
        kwargs = {}
        self.append_params_if_possible(kwargs)
        return kwargs

    def get_pagination_kwargs(self):
        return self.get_list_kwargs()

    def get_mutation_arguments_kwargs(self):
        kwargs = {}
        has_params = self.parameters.get("params", False)
        if has_params:
            input_type = self.parameters["params"].annotation

            class Arguments:
                input = input_type(required=True)

            kwargs["Arguments"] = Arguments
        return kwargs

    def append_params_if_possible(self, kwargs):
        has_params = self.parameters.get("params", False)
        if has_params:
            params_type = self.parameters["params"].annotation
            schema = params_type.schema()
            fields = {
                k: gen_field(k, v, schema) for k, v in schema["properties"].items()
            }
            kwargs["params"] = GraphQLArgument(
                GraphQLNonNull(
                    GraphQLInputObjectType(f"Params{self.name}", fields=fields, )
                )
            )


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
            extra_kwargs = resolver_result.get_item_kwargs()
            field = GraphQLField(
                output,
                args={**extra_kwargs},
                resolve=resolver_result.resolver,
                description=resolver_function.__doc__ or "",
            )
            self.query_fields[f"{name}"] = field
            return field

        return decorate

    def list(self, name, output):
        def decorate(resolver_function):
            resolver_result = parse_resolver(resolver_function, name)
            extra_kwargs = resolver_result.get_list_kwargs()
            field = GraphQLField(
                GraphQLList(output),
                args={**extra_kwargs},
                resolve=resolver_result.resolver,
                description=resolver_function.__doc__ or "nops",
            )
            self.query_fields[f"{name}"] = field
            return field

        return decorate

    def pagination(self, name, output):
        def decorate(resolver_function):
            resolver_result = parse_resolver(resolver_function, name)
            extra_kwargs = resolver_result.get_list_kwargs()
            field = GraphQLField(
                GraphQLObjectType(
                    f"Pagination{name}",
                    fields={
                        "page": GraphQLField(rs.Int),
                        "per_page": GraphQLField(rs.Int),
                        "has_next_page": GraphQLField(rs.Int),
                        "items": GraphQLField(GraphQLList(output)),
                    },
                ),
                args={**extra_kwargs},
                resolve=resolver_result.resolver,
                description=resolver_function.__doc__ or "nops",
            )
            self.query_fields[f"{name}"] = field
            return field

        return decorate

    def mutation(self, name_or_fn, output=None):
        def decorate(resolver_function, name):
            resolver_result = parse_resolver(resolver_function, name)
            extra_kwargs = resolver_result.get_list_kwargs()

            field = GraphQLField(
                output or rs.Boolean,
                args={**extra_kwargs},
                resolve=resolver_result.resolver,
                description=resolver_function.__doc__ or "nops",
            )
            self.mutation_fields[f"{name}"] = field
            return field

        if callable(name_or_fn):
            return decorate(name_or_fn, name_or_fn.__name__)
        return lambda fn: decorate(fn, name_or_fn)

    def build_query(self, type_name):
        return GraphQLObjectType(
            name=type_name,
            fields={name: field for name, field in self.query_fields.items()},
        )

    def build_mutation(self, type_name):
        return GraphQLObjectType(
            name=type_name,
            fields={name: field for name, field in self.mutation_fields.items()},
        )
