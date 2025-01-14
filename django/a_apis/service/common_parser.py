import json

from ninja.errors import HttpError
from ninja.parser import Parser

from django.http import HttpRequest


class CommonParser(Parser):
    @staticmethod
    def no_duplicates_object_pairs_hook(pairs):
        d = {}
        for k, v in pairs:
            if k in d:
                raise ValueError(f"중복된 키가 발견되었습니다: {k}")
            d[k] = v
        return d

    def parse_body(self, request: HttpRequest):
        try:
            return json.loads(
                request.body,
                object_pairs_hook=CommonParser.no_duplicates_object_pairs_hook,
            )
        except ValueError as e:
            raise HttpError(400, str(e))
