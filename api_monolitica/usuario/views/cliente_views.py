from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404

from ..serializers.cliente_serializer import ClienteSerializer
from ..serializers.usuario_serializer import UsuarioSerializer
from cita.models.cita_venta_model import CitaVenta
from cita.models.estado_cita_model import EstadoCita

from ..models.usuario_model import Usuario
from ..models.cliente_model import Cliente

#from utils.permisos import TienePermisoModulo

class ClienteViewSet(viewsets.ModelViewSet):
    queryset = Cliente.objects.all()
    serializer_class = ClienteSerializer
    #permission_classes = [TienePermisoModulo("Cliente")];
    
    # Sobreescribimos el método destroy para cambiar el estado en lugar de eliminar
    def destroy(self, request, *args, **kwargs):
        cliente = self.get_object()
        
        usuario_asociado = cliente.usuario
        
        # Obtener todas las citas de esta cliente
        citas = CitaVenta.objects.filter(cliente_id=cliente)

        # Verificar si hay citas en estado diferente de "Terminada" o "Cancelada"
        
        ids_excluir = EstadoCita.objects.filter(Estado__in=["Terminada", "Cancelada"]).values_list("id", flat=True)
        
        citas_activas = CitaVenta.objects.filter(cliente_id=cliente).exclude(estado_id__in=ids_excluir)

        if citas_activas.exists():
          return Response({
            'message': "No se puede eliminar el cliente porque tiene citas en proceso o pendientes."
          }, status=status.HTTP_400_BAD_REQUEST)

       # Si está activo, desactivar primero
        if usuario_asociado.estado == "Activo":
           usuario_asociado.estado = 'Inactivo'
           usuario_asociado.save()

           cliente.estado = "Inactivo"
           cliente.save()

           return Response({
             'message': 'Cliente y usuario asociado desactivado correctamente'
            }, status=status.HTTP_200_OK)
        else:
           # Desvincular citas (evitar que las borre por error)
           CitaVenta.objects.filter(cliente_id=cliente).update(cliente_id=None)
    
           usuario_asociado.delete()
           cliente.delete()
           return Response({
              'message': "El usuario y cliente fueron eliminados correctamente"
           }, status=status.HTTP_204_NO_CONTENT)
    
    # Acción personalizada para cambiar el estado
    @action(detail=True, methods=['patch'])
    def cambiar_estado(self, request, pk=None):
        cliente = self.get_object()
        usuario_asociado = Usuario.objects.get(id = cliente.usuario_id)
        nuevo_estado = "Activo" if cliente.estado == "Inactivo" else "Inactivo"
        usuario_asociado.estado = nuevo_estado
        
        cliente.estado = nuevo_estado
        cliente.save()
        usuario_asociado.save()
        serializer = self.get_serializer(cliente)
        return Response({"message": f"Estado del cliente cambiado a {nuevo_estado}", "data": serializer.data})
    
    # Filtrar clientes por estado
    @action(detail=False, methods=['get'])
    def activos(self, request):
        clientes_activos = Cliente.objects.filter(estado="activo")
        serializer = self.get_serializer(clientes_activos, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def inactivos(self, request):
        clientes_inactivos = Cliente.objects.filter(estado="Inactivo")
        serializer = self.get_serializer(clientes_inactivos, many=True)
        return Response(serializer.data)
    
    # Buscar cliente por número de documento
    @action(detail=False, methods=['get'])
    def por_documento(self, request):
        numero = request.query_params.get('numero', None)
        tipo = request.query_params.get('tipo', None)
        
        if numero:
            query = {'numero_documento': numero}
            if tipo:
                query['tipo_documento'] = tipo
                
            clientes = Cliente.objects.filter(**query)
            serializer = self.get_serializer(clientes, many=True)
            return Response(serializer.data)
        return Response({"error": "Debe especificar un número de documento"}, status=status.HTTP_400_BAD_REQUEST)