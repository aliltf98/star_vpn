from django.urls import path
from .views import *

urlpatterns = [
    path("", home, name="home"),
    path("pages/<int:id>/", pages, name="page_detail")
]
