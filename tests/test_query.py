from typing import List
from typing import Optional

from django.http.request import HttpRequest
from django.http.response import JsonResponse
from django.test import override_settings
from django.urls import path
from django.views import View
from django_autowired.autowired import autowired
from django_autowired.param_func import Path
from django_autowired.param_func import Query
from tests.base import BaseTestCase


class ClassQueryView(View):
    @autowired(description="this is class-query view")
    def get(
        self,
        request: HttpRequest,
        name: str,
        id: int = Path(..., gt=20),
        limit: Optional[int] = 100,
        page: Optional[int] = Query(default=11, ge=10, le=20),
    ):
        return JsonResponse(data={"id": id, "name": name, "limit": limit, "page": page})


class AliasQueryView(View):
    @autowired(description="this is alias-query view")
    def get(
        self, request: HttpRequest, q: Optional[str] = Query(None, alias="item-query")
    ):
        return JsonResponse(data={"q": q})


class MultiValueQueryView(View):
    @autowired(description="this is multi-value-query view")
    def get(self, request: HttpRequest, q: Optional[List[str]] = Query(["one", "two"])):
        return JsonResponse(data={"q": q})


@autowired(description="this is func-query view")
def func_query_view(
    request: HttpRequest,
    name: str,
    id: int = Path(..., gt=30, le=40),
    limit: Optional[int] = 100,
    page: Optional[int] = Query(default=11, ge=10, le=20),
):
    return JsonResponse(data={"id": id, "name": name, "limit": limit, "page": page})


urlpatterns = [
    path(route="class-query/<int:id>/", view=ClassQueryView.as_view()),
    path(route="func-query/<int:id>/", view=func_query_view),
    path(route="alias-query/", view=AliasQueryView.as_view()),
    path(route="multi-value-query/", view=MultiValueQueryView.as_view()),
]


@override_settings(ROOT_URLCONF="tests.test_query")
class TestClassQueryView(BaseTestCase):
    def test_non_default_success(self):
        data = self.method_json_expect_code(
            method=self.GET,
            code=200,
            url="/class-query/21/",
            data={
                "name": "bea",
            },
        )
        assert data["id"] == 21
        assert data["name"] == "bea"
        assert data["limit"] == 100
        assert data["page"] == 11

    def test_default_success(self):
        data = self.method_json_expect_code(
            method=self.GET,
            code=200,
            url="/class-query/21/",
            data={"name": "bea", "limit": 99},
        )
        assert data["id"] == 21
        assert data["name"] == "bea"
        assert data["limit"] == 99

    def test_default_error(self):
        self.method_json_expect_code(
            method=self.GET,
            code=400,
            url="/class-query/21/",
            data={"name": "bea", "page": 8},
        )

    def test_validate_error(self):
        self.method_json_expect_code(
            method=self.GET, code=400, url="/class-query/10/", data={}
        )
        self.method_json_expect_code(
            method=self.GET, code=400, url="/class-query/21/", data={}
        )


@override_settings(ROOT_URLCONF="tests.test_query")
class TestFuncPathView(BaseTestCase):
    def test_non_default_success(self):
        data = self.method_json_expect_code(
            method=self.GET,
            code=200,
            url="/func-query/33/",
            data={
                "name": "bea",
            },
        )
        assert data["id"] == 33
        assert data["name"] == "bea"
        assert data["limit"] == 100
        assert data["page"] == 11

    def test_default_success(self):
        data = self.method_json_expect_code(
            method=self.GET,
            code=200,
            url="/func-query/34/",
            data={"name": "bea", "limit": 99},
        )
        assert data["id"] == 34
        assert data["name"] == "bea"
        assert data["limit"] == 99

    def test_default_error(self):
        self.method_json_expect_code(
            method=self.GET,
            code=400,
            url="/func-query/34/",
            data={"name": "bea", "page": 8},
        )

    def test_validate_error(self):
        self.method_json_expect_code(
            method=self.GET, code=400, url="/func-query/10/", data={}
        )
        self.method_json_expect_code(
            method=self.GET, code=400, url="/func-query/21/", data={}
        )


@override_settings(ROOT_URLCONF="tests.test_query")
class TestAliasQueryView(BaseTestCase):
    def test_success(self):
        data = self.method_json_expect_code(
            method=self.GET,
            code=200,
            url="/alias-query/",
            data={
                "item-query": "bea",
            },
        )
        assert data["q"] == "bea"

    def test_success1(self):
        data = self.method_json_expect_code(
            method=self.GET,
            code=200,
            url="/alias-query/",
            data={},
        )
        assert data["q"] is None


@override_settings(ROOT_URLCONF="tests.test_query")
class TestMultiValueQueryView(BaseTestCase):
    def test_success(self):
        data = self.method_json_expect_code(
            method=self.GET,
            code=200,
            url="/multi-value-query/",
            data={
                "q": ["a", "b"],
            },
        )
        self.assertListEqual(["a", "b"], data["q"])

    def test_default(self):
        data = self.method_json_expect_code(
            method=self.GET,
            code=200,
            url="/multi-value-query/",
            data={},
        )
        self.assertListEqual(["one", "two"], data["q"])
