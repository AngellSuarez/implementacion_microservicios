# Create your views here.
from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Servicio

#ya no se usando dado que es una base de datos distinta

# from cita.models.servicio_cita import ServicioCita
# from cita.models.estado_cita import EstadoCita

from .serializer import ServicioSerializer
from utils.permisos import TienePermisoModulo


# Create your views here.
class ServicioViewSet(viewsets.ModelViewSet):
    queryset = Servicio.objects.all()
    serializer_class = ServicioSerializer
    permission_classes = [TienePermisoModulo("Servicio")];

    def destroy(self, request, *args, **kwargs):
        try:
            servicio = self.get_object()
            if servicio.estado == "Activo":
                servicio.estado == "Inactivo"
                servicio.save()
                return Response({'message':"Servicio desactivado correctamente"},status=status.HTTP_200_OK)
            else:
                servicio.delete()
                return Response({'message':"Servicio eliminado con exito"},status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({'message':f"Ocurrio un erro al eliminar el servicio: {e}"},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['patch'])
    def cambiar_estado(self, request, pk=None):
        servicio = self.get_object()
        nuevo_estado = "Activo" if servicio.estado == "Inactivo" else "Inactivo"
        servicio.estado = nuevo_estado
        servicio.save()
        serializer = self.get_serializer(servicio)
        return Response({"message": f"Estado del servicio cambiado a {nuevo_estado}", "data": serializer.data})