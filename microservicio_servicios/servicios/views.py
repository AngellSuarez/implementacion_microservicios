from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated

from .models import Servicio
from .serializer import ServicioSerializer
from utils.permisos import TienePermisoModulo

from rest_framework import permissions


class ServicioViewSet(viewsets.ModelViewSet):
    queryset = Servicio.objects.all()
    serializer_class = ServicioSerializer

    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated(), TienePermisoModulo("Servicio")]


    def destroy(self, request, *args, **kwargs):
        try:
            servicio = self.get_object()
            if servicio.estado == "Activo":
                servicio.estado = "Inactivo"
                servicio.save()
                return Response(
                    {'message': "Servicio desactivado correctamente"},
                    status=status.HTTP_200_OK
                )
            else:
                servicio.delete()
                return Response(
                    {'message': "Servicio eliminado con éxito"},
                    status=status.HTTP_204_NO_CONTENT
                )
        except Exception as e:
            return Response(
                {'message': f"Ocurrió un error al eliminar el servicio: {e}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['patch'])
    def cambiar_estado(self, request, pk=None):
        try:
            servicio = self.get_object()
            nuevo_estado = "Activo" if servicio.estado == "Inactivo" else "Inactivo"
            servicio.estado = nuevo_estado
            servicio.save()
            serializer = self.get_serializer(servicio)
            return Response({
                "message": f"Estado del servicio cambiado a {nuevo_estado}",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {'message': f"Ocurrió un error al cambiar el estado del servicio: {e}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )