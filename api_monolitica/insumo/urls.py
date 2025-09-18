from django.urls import path,include
from rest_framework.routers import DefaultRouter
from .views import MarcaViewSet, InsumoViewSet

router = DefaultRouter()
router.register(r"marcas",MarcaViewSet,basename="marcas")
router.register(r"insumos",InsumoViewSet,basename="insumos")

urlpatterns = [
    path('',include(router.urls))
]