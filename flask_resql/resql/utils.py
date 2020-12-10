from random import randint
from typing import Union, Dict, Any

from graphql import (
    GraphQLField,
    GraphQLInputField,
    GraphQLNonNull,
    GraphQLArgument,
    GraphQLEnumType,
    GraphQLList,
)
from pydantic.main import BaseModel

from flask_resql import resql as rs
from flask_resql.resql import InputObjectType, ObjectType


def force_resolve_attr(obj: Union[Dict, Any], name: str):
    if obj is None:
        return None
    if isinstance(obj, dict):
        return obj.get(name, None)
    return getattr(obj, name, None)


def create_input_field(field_name, field_type, required=False) -> GraphQLInputField:
    if not required:
        return GraphQLInputField(field_type, out_name=field_name)
    else:
        return GraphQLInputField(GraphQLNonNull(field_type), out_name=field_name)


def transform_validator_field(field_name, field_schema, required=False):
    if field_schema["type"] == "string":
        if field_schema.get("format", None) == "date":
            return create_input_field(field_name, rs.Date, required)
        if field_schema.get("format", None) == "date-time":
            return create_input_field(field_name, rs.DateTime, required)
        return create_input_field(field_name, rs.String, required)
    if field_schema["type"] == "integer":
        return create_input_field(field_name, rs.Int, required)
    """
    if v["type"] == "integer"
    # TODO: nested support
    """
    raise NotImplementedError


def get_simple_resolver(field_name):
    return lambda root, _: force_resolve_attr(root, field_name)


def create_scalar_field(field_name, field_type, use_list=False, description="无"):
    if use_list:
        field_type = GraphQLList(field_type)
    return GraphQLField(
        field_type, resolve=get_simple_resolver(field_name), description=description
    )


from devtools import debug


def transform_serializer_field(path, name, schema, parent_schema, global_schema):
    # 初始 Node 无 Parent
    if not parent_schema:
        parent_schema = schema
    if not global_schema:
        global_schema = schema
    # TODO: ban list of list
    schema_type = parent_schema.get("type", None)

    use_list = schema_type == "array"

    field_description = schema.get("description", None)
    schema_type = schema.get("type", None)
    description = schema.get("description", None)
    if use_list:
        description = parent_schema.get("description", "无")

    if schema.get("$ref", None):
        type_name = schema["$ref"].replace("#/definitions/", "")
        definitions = global_schema.get("definitions", {})
        return transform_serializer_field(
            f"{path}", name, definitions[type_name], parent_schema, global_schema
        )

    if schema_type == "object":
        properties = schema.get("properties", {})
        fields = {}
        debug(
            schema, parent_schema, description,
        )
        for field_name, field_schema in properties.items():
            fields[field_name] = transform_serializer_field(
                f"{path}/{field_name}",
                field_name,
                field_schema,
                schema,
                global_schema,  # TODO: use list
            )
        if use_list:
            return GraphQLField(
                GraphQLList(ObjectType(name, fields=fields, description=field_description)),
                resolve=get_simple_resolver(name),
                description=description,
            )
        return ObjectType(name, fields=fields, description=description)

    if schema.get("enum", None):
        field_type = GraphQLEnumType(
            f"{name}_{randint(1, 200)}",
            values=dict(zip(schema["enum"], schema["enum"])),
            description=field_description
        )

        return create_enum_field(name, field_type, use_list, description)
    if schema_type == "string":
        if schema.get("format", None) == "date":
            return create_scalar_field(name, rs.Date, use_list, description)
        if schema.get("format", None) == "date-time":
            return create_scalar_field(name, rs.DateTime, use_list, description)
        return create_scalar_field(name, rs.String, use_list, description)
    if schema_type == "integer":
        return create_scalar_field(name, rs.Int, use_list, description)
    if schema_type == "array":
        return transform_serializer_field(
            f"{path}", name, schema["items"], schema, global_schema
        )
    raise NotImplementedError


def create_enum_field(name, field_type, use_list, description=""):
    if use_list:
        field_type = GraphQLList(field_type)
    return GraphQLField(
        field_type, resolve=get_simple_resolver(name), description=description
    )


def gen_serialize_field(field_name: str, field_type):
    return GraphQLField(
        field_type, resolve=lambda root, info: force_resolve_attr(root, field_name)
    )


def gen_args_from_params(name: str, params_type: BaseModel) -> GraphQLArgument:
    schema = params_type.schema()
    fields = {}
    required_field_names = schema.get("required", [])
    for field_name, field_schema in schema["properties"].items():
        fields[field_name] = transform_validator_field(
            field_name, field_schema, field_name in required_field_names
        )
    return GraphQLArgument(
        GraphQLNonNull(InputObjectType(f"params_{name}", fields=fields, ))
    )
