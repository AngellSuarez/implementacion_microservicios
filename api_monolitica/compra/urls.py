from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views.estado_compra import EstadoCompraViewSet
from .views.compra import CompraViewSet
from .views.compra_insumo import CompraInsumoViewSet

router = DefaultRouter()
router.register(r"estado-compra",EstadoCompraViewSet,basename="Estado cita")
router.register(r"compras",CompraViewSet,basename="compras")
router.register(r"compra-insumos",CompraInsumoViewSet,basename="compra-insumos")

urlpatterns = [
    path('',include(router.urls))
]