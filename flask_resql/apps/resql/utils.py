from random import randint
from typing import Union, Dict, Any

from graphql import GraphQLField, GraphQLInputField, GraphQLNonNull, GraphQLArgument
from pydantic.main import BaseModel

from flask_resql.apps import resql as rs
from flask_resql.apps.resql import InputObjectType, ObjectType


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


def create_field(field_name: str, field_type, required=False):
    return GraphQLField(field_type, resolve=lambda root, info: force_resolve_attr(root, field_name))


def transform_serializer_field(field_name, field_schema, required=False, definitions=None):
    if field_schema.get("$ref", None):
        name = field_schema["$ref"].replace("#/definitions/", "")
        return transform_serializer_model(field_name + f"{randint(1, 100)}", definitions[name])
    if field_schema["type"] == "string":
        if field_schema.get("format", None) == "date":
            return create_field(field_name, rs.Date, required)
        if field_schema.get("format", None) == "date-time":
            return create_field(field_name, rs.DateTime, required)
        return create_field(field_name, rs.String, required)
    if field_schema["type"] == "integer":
        return create_field(field_name, rs.Int, required)
    # if field_schema["type"] == "array":
    #     return create_field(field_name, rs.Int, required)
    """
    if v["type"] == "integer"
    # TODO: nested support
    """
    raise NotImplementedError


def transform_serializer_model(type_name, model_schema, calls=5):
    properties = model_schema["properties"]
    definitions = model_schema.get("definitions", {})

    fields = {}
    for name, schema in properties.items():
        fields[name] = transform_serializer_field(
            name,
            schema,
            False,
            definitions
        )
    return ObjectType(
        type_name,
        fields=fields,
    )


def gen_serialize_field(field_name: str, field_type):
    return GraphQLField(field_type, resolve=lambda root, info: force_resolve_attr(root, field_name))


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
