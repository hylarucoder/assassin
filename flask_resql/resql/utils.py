from random import randint
from typing import Union, Dict, Any

from graphql import GraphQLField, GraphQLInputField, GraphQLNonNull, GraphQLArgument, GraphQLEnumType
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


def create_field(field_name: str, field_type, required=False):
    return GraphQLField(
        field_type, resolve=lambda root, info: force_resolve_attr(root, field_name)
    )


def transform_serializer_field(
        path, name, schema, model_schema, required=False
):
    if schema.get("$ref", None):
        # sub model
        # enum
        return transform_serializer_model(
            f"{path}/{name}",
            name,
            schema,
            model_schema,
        )
    # if schema["type"] == "object":
    #     pass
    if schema["type"] == "string":
        if schema.get("format", None) == "date":
            return create_field(name, rs.Date, required)
        if schema.get("format", None) == "date-time":
            return create_field(name, rs.DateTime, required)
        return create_field(name, rs.String, required)
    if schema["type"] == "integer":
        return create_field(name, rs.Int, required)
    # if field_schema["type"] == "array":
    #     return create_field(field_name, rs.Int, required)
    """
    if v["type"] == "integer"
    # TODO: nested support
    """
    raise NotImplementedError


def transform_serializer_model(path, name, schema, model_schema=None):
    # /
    if not model_schema:
        model_schema = schema
    print("type->", name, model_schema)
    schema_type = schema.get("type", None)
    if schema_type == "object":
        properties = schema.get("properties", {})
        fields = {}
        for field_name, field_schema in properties.items():
            fields[field_name] = transform_serializer_field(
                f"{path}/{field_name}",
                field_name,
                field_schema,
                model_schema,
                False
            )
        return ObjectType(name, fields=fields, )
    if schema.get("enum", None):
        type_name = schema["$ref"].replace("#/definitions/", "")
        # print(model_schema, "----><<><><")
        # TODO: 可能需要吧 basemodel传递过来？
        return GraphQLField(
            GraphQLEnumType("EEnumasdasd", values=dict(zip(model_schema["enum"], model_schema["enum"]))))
    # ref
    # sub model
    # enum
    print("--111-->", schema)

    type_name = schema["$ref"].replace("#/definitions/", "")
    definitions = model_schema.get("definitions", {})
    return transform_serializer_model(path, name, definitions[type_name], model_schema=model_schema)


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
