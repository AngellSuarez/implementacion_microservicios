from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views.estado_cita_view import EstadoCitaViewSet
from .views.cita_venta_view import CitaVentaViewSet
from .views.servicio_cita_view import ServicioCitaViewSet

router = DefaultRouter()
router.register(r'estados-cita', EstadoCitaViewSet)
router.register(r'citas-venta', CitaVentaViewSet, basename='citas-venta')
router.register(r'servicios-cita', ServicioCitaViewSet)

urlpatterns = [
    path('', include(router.urls)),
]