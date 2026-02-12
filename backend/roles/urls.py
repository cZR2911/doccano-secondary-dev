from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import FeatureViewSet, RoleViewSet

router = DefaultRouter(trailing_slash=False)
router.register("roles", RoleViewSet, basename="role")
router.register("features", FeatureViewSet, basename="feature")

urlpatterns = router.urls
