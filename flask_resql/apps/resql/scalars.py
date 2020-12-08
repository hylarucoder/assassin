import graphql as gql


def serialize(v):
    return v


def coerce(v):
    return v


def parse(v):
    return v


ID = gql.GraphQLID

Int = gql.GraphQLInt

Float = gql.GraphQLFloat

String = gql.GraphQLString

Boolean = gql.GraphQLBoolean

Currency = gql.GraphQLScalarType(
    name="Currency",
    description="Currency",
    serialize=serialize,
    parse_value=coerce,
    parse_literal=parse,
)

Date = gql.GraphQLScalarType(
    name="Date",
    description="Date",
    serialize=serialize,
    parse_value=coerce,
    parse_literal=parse,
)

DateTime = gql.GraphQLScalarType(
    name="DateTime",
    description="DateTime",
    serialize=serialize,
    parse_value=coerce,
    parse_literal=parse,
)

Mobile = gql.GraphQLScalarType(
    name="Mobile",
    description="Mobile",
    serialize=serialize,
    parse_value=coerce,
    parse_literal=parse,
)
