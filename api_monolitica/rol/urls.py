# rol/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views.rol_view import RolViewSet
from .views.permiso_view import PermisoViewSet
from .views.permiso_rol_view import PermisoRolViewSet

router = DefaultRouter()
router.register(r'roles', RolViewSet, basename='rol')
router.register(r'permiso', PermisoViewSet, basename='permiso')
router.register(r'permisos-rol', PermisoRolViewSet, basename='permiso-rol')

urlpatterns = [
    path('', include(router.urls)),
]
