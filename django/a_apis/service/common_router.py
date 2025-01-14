from typing import Any, List, Optional

from ninja.operation import Operation, PathView
from ninja.parser import Parser
from ninja.router import Router

from django.http import HttpRequest
from django.http.response import HttpResponseBase


class CustomRouter(Router):
    def __init__(self):
        super().__init__()

    def post(self, path: str, *, parser: Optional[Parser] = None, **kwargs):
        return super().post(path, parser=parser, **kwargs)

    def api_operation(
        self,
        methods: List[str],
        path: str,
        *,
        parser: Optional[Parser] = None,
        **kwargs,
    ):
        return super().api_operation(methods, path, parser=parser, **kwargs)

    def add_api_operation(
        self,
        *args,
        parser: Optional[Parser] = None,
        **kwargs,
    ):
        return super().add_api_operation(*args, parser=parser, **kwargs)


class CustomOperation(Operation):
    def __init__(self, *args, parser: Optional[Parser] = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.parser = parser or Parser()


def run(self, request: HttpRequest, **kw: Any) -> HttpResponseBase:
    if request.body:
        try:
            self.parser.parse_body(request)
        except Exception as e:
            return self.api.on_exception(request, e)


class CustomPathView(PathView):
    def add_operation(self, *args, parser: Optional[Parser] = None, **kwargs):
        operation = CustomOperation(*args, parser=parser, **kwargs)
        return super().add_operation(operation)
