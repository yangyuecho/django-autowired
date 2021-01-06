from django.http.request import HttpRequest
from django.http.response import JsonResponse
from django.views import View
from django_autowired.autowired import autowired
from django_autowired.param_func import Body
from pydantic import BaseModel


class Items(BaseModel):
    name: str


class FooView(View):
    @autowired(response_model=Items)
    def post(
        self,
        request: HttpRequest,
        items: Items = Body(..., embed=True),
    ):
        return JsonResponse(items)
