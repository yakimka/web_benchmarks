import os

from django.urls import path

from . import async_views, views

ASYNC_MODE = os.getenv("ASYNC_MODE") == "1"

bench_views = async_views if ASYNC_MODE else views

urlpatterns = [
    path("plaintext", bench_views.plaintext, name="plaintext"),
    path("api", bench_views.api, name="api"),
    path("db", bench_views.db, name="db"),
]
