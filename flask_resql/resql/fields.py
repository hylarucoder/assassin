from typing import Optional, Collection, Dict, Any

from graphql import (
    GraphQLInputObjectType,
    GraphQLObjectType,
    GraphQLFieldMap,
    Thunk,
    GraphQLInterfaceType,
    GraphQLIsTypeOfFn,
    ObjectTypeDefinitionNode,
    ObjectTypeExtensionNode,
    GraphQLInputFieldMap,
    InputObjectTypeDefinitionNode,
    InputObjectTypeExtensionNode,
)
from graphql.pyutils import snake_to_camel
from graphql.type.definition import GraphQLInputFieldOutType


class ObjectType(GraphQLObjectType):
    def __init__(
        self,
        name: str,
        fields: Thunk[GraphQLFieldMap],
        interfaces: Optional[Thunk[Collection["GraphQLInterfaceType"]]] = None,
        is_type_of: Optional[GraphQLIsTypeOfFn] = None,
        extensions: Optional[Dict[str, Any]] = None,
        description: Optional[str] = None,
        ast_node: Optional[ObjectTypeDefinitionNode] = None,
        extension_ast_nodes: Optional[Collection[ObjectTypeExtensionNode]] = None,
    ) -> None:
        fields = {snake_to_camel(k, False): v for k, v in fields.items()}
        name = snake_to_camel(name)
        super().__init__(
            name,
            fields,
            interfaces,
            is_type_of,
            extensions,
            description,
            ast_node,
            extension_ast_nodes,
        )


class InputObjectType(GraphQLInputObjectType):
    def __init__(
        self,
        name: str,
        fields: Thunk[GraphQLInputFieldMap],
        description: Optional[str] = None,
        out_type: Optional[GraphQLInputFieldOutType] = None,
        extensions: Optional[Dict[str, Any]] = None,
        ast_node: Optional[InputObjectTypeDefinitionNode] = None,
        extension_ast_nodes: Optional[Collection[InputObjectTypeExtensionNode]] = None,
    ) -> None:
        fields = {snake_to_camel(k, False): v for k, v in fields.items()}
        name = snake_to_camel(name)
        super().__init__(
            name,
            fields,
            description,
            out_type,
            extensions,
            ast_node,
            extension_ast_nodes,
        )
