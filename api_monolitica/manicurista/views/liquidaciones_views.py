from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db.models import Max

from ..models.liquidacion_model import Liquidacion
from ..serializers.liquidacion_serializer import LiquidacionSerializer

from utils.permisos import TienePermisoModulo

class LiquidacionViewSet(viewsets.ModelViewSet):
    serializer_class = LiquidacionSerializer
    queryset = Liquidacion.objects.all()
    permission_classes = [TienePermisoModulo("Liquidacion")];

    def get_queryset(self):
        manicurista_id = self.request.query_params.get('manicurista_id')
        if manicurista_id:
            return Liquidacion.objects.filter(manicurista_id=manicurista_id)
        return Liquidacion.objects.all()
    
    @action(detail =False, methods=['get'], url_path ='ultimas-liquidaciones')
    def ultimas_liquidaciones(self,request):
        datos = (
            Liquidacion.objects.values('manicurista_id').annotate(ultima_fecha=Max('FechaFinal'))
        )
        
        return Response(list(datos),status=status.HTTP_200_OK)