import inspect
import typing
from typing import Callable, Dict, Any

from flask_resql import resql as rs
from flask_resql.resql import gen_args_from_params


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
