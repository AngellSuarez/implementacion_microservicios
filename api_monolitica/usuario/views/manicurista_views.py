from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404

from ..serializers.manicurista_serializer import ManicuristaSerializer
from ..serializers.usuario_serializer import UsuarioSerializer
from cita.models.cita_venta_model import CitaVenta
from cita.models.estado_cita_model import EstadoCita

from ..models.usuario_model import Usuario
from ..models.manicurista_model import Manicurista

from utils.permisos import TienePermisoModulo

class ManicuristaViewSet(viewsets.ModelViewSet):
    queryset = Manicurista.objects.all()
    serializer_class = ManicuristaSerializer
    permission_classes = [TienePermisoModulo("Manicurista")];
    
    # Sobreescribimos el método destroy para cambiar el estado en lugar de eliminar
    def destroy(self, request, *args, **kwargs):
        manicurista = self.get_object()
        usuario_asociado = manicurista.usuario

        # Obtener todas las citas de esta manicurista
        citas = CitaVenta.objects.filter(manicurista_id=manicurista)

        # Verificar si hay citas en estado diferente de "Terminada" o "Cancelada"
        
        ids_excluir = EstadoCita.objects.filter(Estado__in=["Terminada", "Cancelada"]).values_list("id", flat=True)

        citas_activas = CitaVenta.objects.filter(manicurista_id=manicurista).exclude(estado_id__in=ids_excluir)

        if citas_activas.exists():
          return Response({
            'message': "No se puede eliminar la manicurista porque tiene citas en proceso o pendientes."
          }, status=status.HTTP_400_BAD_REQUEST)

        # Si está activo, desactivar primero
        if usuario_asociado.estado == "Activo":
           usuario_asociado.estado = 'Inactivo'
           usuario_asociado.save()

           manicurista.estado = "Inactivo"
           manicurista.save()

           return Response({
             'message': 'Manicurista y usuario asociado desactivado correctamente'
            }, status=status.HTTP_200_OK)
        else:
           # Desvincular citas (evitar que las borre por error)
           CitaVenta.objects.filter(manicurista_id=manicurista).update(manicurista_id=None)
    
           usuario_asociado.delete()
           manicurista.delete()
           return Response({
              'message': "El usuario y manicurista fueron eliminados correctamente"
           }, status=status.HTTP_204_NO_CONTENT)

    # Acción personalizada para cambiar el estado
    @action(detail=True, methods=['patch'])
    def cambiar_estado(self, request, pk=None):
        
        manicurista = self.get_object()
        usuario_asociado = Usuario.objects.get(id = manicurista.usuario_id)
        
        nuevo_estado = "Activo" if manicurista.estado == "Inactivo" else "Inactivo"
        manicurista.estado = nuevo_estado
        usuario_asociado.estado = nuevo_estado
        
        manicurista.save()
        usuario_asociado.save()
        serializer = self.get_serializer(manicurista)
        return Response({"message": f"Estado del manicurista cambiado a {nuevo_estado}", "data": serializer.data})
    
    # Filtrar manicuristas por estado
    @action(detail=False, methods=['get'])
    def activos(self, request):
        manicuristas_activos = Manicurista.objects.filter(estado="Activo")
        serializer = self.get_serializer(manicuristas_activos, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def inactivos(self, request):
        manicuristas_inactivos = Manicurista.objects.filter(estado="Inactivo")
        serializer = self.get_serializer(manicuristas_inactivos, many=True)
        return Response(serializer.data)
    
    # Buscar manicurista por número de documento
    @action(detail=False, methods=['get'])
    def por_documento(self, request):
        numero = request.query_params.get('numero', None)
        tipo = request.query_params.get('tipo', None)
        
        if numero:
            query = {'numero_documento': numero}
            if tipo:
                query['tipo_documento'] = tipo
                
            manicuristas = Manicurista.objects.filter(**query)
            serializer = self.get_serializer(manicuristas, many=True)
            return Response(serializer.data)
        return Response({"error": "Debe especificar un número de documento"}, status=status.HTTP_400_BAD_REQUEST)
    
    # Filtrar manicuristas por fecha de contratación
    @action(detail=False, methods=['get'])
    def por_fecha_contratacion(self, request):
        desde = request.query_params.get('desde', None)
        hasta = request.query_params.get('hasta', None)
        
        query = {}
        if desde:
            query['fecha_contratacion__gte'] = desde
        if hasta:
            query['fecha_contratacion__lte'] = hasta
            
        if query:
            manicuristas = Manicurista.objects.filter(**query)
            serializer = self.get_serializer(manicuristas, many=True)
            return Response(serializer.data)
        return Response({"error": "Debe especificar al menos una fecha (desde o hasta)"}, status=status.HTTP_400_BAD_REQUEST)