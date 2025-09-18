from ..models.estado_compra import EstadoCompra
from ..serializers.estado_compra import EstadoCompraSerializer
from rest_framework import viewsets

class EstadoCompraViewSet(viewsets.ModelViewSet):
    queryset = EstadoCompra.objects.all()
    serializer_class = EstadoCompraSerializer