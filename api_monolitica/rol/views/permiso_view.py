from rest_framework import viewsets, status, permissions;
from rest_framework.response import Response;
from rest_framework.decorators import action;
from rest_framework.permissions import AllowAny;

from ..models import Permiso;
from ..serializers import PermisoSerializer;

class PermisoViewSet(viewsets.ModelViewSet):
    queryset = Permiso.objects.all();
    serializer_class = PermisoSerializer;
    permission_classes = [AllowAny];
