from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views.usuario_views import UsuarioViewSet
from .views.cliente_views import ClienteViewSet
from .views.manicurista_views import ManicuristaViewSet

router = DefaultRouter()
router.register(r'usuarios', UsuarioViewSet)
router.register(r'clientes', ClienteViewSet)
router.register(r'manicuristas', ManicuristaViewSet)

urlpatterns = [
    path('', include(router.urls)),
]