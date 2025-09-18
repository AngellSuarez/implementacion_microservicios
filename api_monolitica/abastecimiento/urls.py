
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views.abastecimientoView import AbastecimientoViewSet
from .views.InsumoAbastecimientoView import InsumoAbastecimientoViewSet

router = DefaultRouter()
router.register(r'abastecimientos', AbastecimientoViewSet, basename='abastecimiento')
router.register(r'insumo-abastecimientos', InsumoAbastecimientoViewSet, basename='insumoabastecimiento')

urlpatterns = [
    path('', include(router.urls)),
]