from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import TodoViewSet, health

router = DefaultRouter()
router.register(r"todos", TodoViewSet, basename="todo")

urlpatterns = [
    path("health/", health, name="health"),
    *router.urls,
]
