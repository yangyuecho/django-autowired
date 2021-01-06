from django.urls import path
from django_autowired.autowired import autowired

from .views import FooView

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
autowired.setup_schema()
urlpatterns = [
    path(route="openapi.json", view=autowired.get_openapi_view()),
    path(route="swagger", view=autowired.get_swagger_ui_view()),
    path(route="items/", view=FooView.as_view()),
]
