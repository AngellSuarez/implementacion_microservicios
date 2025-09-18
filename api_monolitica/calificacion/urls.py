from django.urls import path
from .views import CalificacionListCreateAPIView

urlpatterns = [
    path('', CalificacionListCreateAPIView.as_view(), name='listar_y_crear_calificaciones'),
]
