from django.urls import include, path

urlpatterns = [
    path("", include("bench.urls")),
    # path("admin/", admin.site.urls),
]
