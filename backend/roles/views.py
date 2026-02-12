from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser, IsAuthenticated

from .models import Feature, Role
from .serializers import FeatureSerializer, RoleSerializer


class RoleViewSet(viewsets.ModelViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    pagination_class = None

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]


class FeatureViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Feature.objects.all()
    serializer_class = FeatureSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None
