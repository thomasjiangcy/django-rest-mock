from django.urls import re_path

from .views import SomeView


urlpatterns = [
    re_path(r'^view1/$', SomeView.as_view())
]
