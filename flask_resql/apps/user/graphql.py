import datetime
import traceback
from typing import Dict, Any, Union, List

from graphql import GraphQLError
from graphql_server.flask import GraphQLView

import orjson

datetime_fmt = "%Y-%m-%d %H:%M:%S"
date_fmt = "%Y-%m-%d"
time_fmt = "%H:%M:%S"


def default_encoder(obj):
    if isinstance(obj, datetime.datetime):
        return obj.strftime(datetime_fmt)
    if isinstance(obj, datetime.date):
        return obj.strftime(date_fmt)
    if isinstance(obj, datetime.time):
        return obj.strftime(time_fmt)
    return obj


def json_encode(data: Union[Dict, List], pretty: bool = False) -> str:
    if not pretty:
        return orjson.dumps(
            data,
            option=orjson.OPT_PASSTHROUGH_DATETIME,
            default=default_encoder
        ).decode()
    return orjson.dumps(
        data,
        option=orjson.OPT_PASSTHROUGH_DATETIME,
        default=default_encoder
    ).decode()


class WGraphQLView(GraphQLView):
    encode = staticmethod(json_encode)

    @staticmethod
    def format_error(error: GraphQLError) -> Dict[str, Any]:
        """Format a GraphQL error.

        Given a GraphQLError, format it according to the rules described by the "Response
        Format, Errors" section of the GraphQL Specification.
        """
        if not isinstance(error, GraphQLError):
            raise TypeError("Expected a GraphQLError.")
        formatted: Dict[str, Any] = dict(  # noqa: E701 (pycqa/flake8#394)
            message=error.message or "An unknown error occurred.",
            locations=(
                [location.formatted for location in error.locations]
                if error.locations is not None
                else None
            ),
            path=error.path,
            traceback=str(traceback.print_tb(error.__traceback__)),
        )
        if error.extensions:
            formatted.update(extensions=error.extensions)
        return formatted

    pass
