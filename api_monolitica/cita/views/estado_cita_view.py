from ..models.estado_cita_model import EstadoCita
from ..serializers.estado_cita_serializer import EstadoCitaSerializer
from rest_framework import viewsets

class EstadoCitaViewSet(viewsets.ModelViewSet):
    queryset = EstadoCita.objects.all()
    serializer_class = EstadoCitaSerializer