from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404

from ..serializers.usuario_serializer import UsuarioSerializer
from ..models.usuario_model import Usuario

from ..models.cliente_model import Cliente
from ..models.manicurista_model import Manicurista
from rol.models import Rol

from utils.permisos import TienePermisoModulo

class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer
    permission_classes = [TienePermisoModulo("Usuario")];

    
    def destroy(self, request, *args, **kwargs):
        try:
            usuario = self.get_object()
            usuario_id = usuario.id
    
            if usuario.estado == "Activo":
                usuario.estado = 'Inactivo'
                usuario.save()
    
                try:
                    cliente = Cliente.objects.get(usuario_id=usuario_id)
                    cliente.estado = 'Inactivo'
                    cliente.save()
                except Cliente.DoesNotExist:
                    pass
                
                try:
                    manicurista = Manicurista.objects.get(usuario_id=usuario_id)
                    manicurista.estado = 'Inactivo'
                    manicurista.save()
                except Manicurista.DoesNotExist:
                    pass
                
                return Response({'message': 'Usuario y sus asociados desactivados correctamente'}, status=status.HTTP_200_OK)
            else:
                usuario.delete()
                try:
                    cliente = Cliente.objects.get(usuario_id=usuario_id)
                    cliente.delete()
                except Cliente.DoesNotExist:
                    pass
                
                try:
                    manicurista = Manicurista.objects.get(usuario_id=usuario_id)
                    manicurista.delete()
                except Manicurista.DoesNotExist:
                    pass
                
                return Response({'message': 'Usuario y sus asociados eliminados permanentemente'}, status=status.HTTP_204_NO_CONTENT)
    
        except Exception as e:
            return Response({'message': f'Ocurrió un error: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)        
    
    # Acción personalizada para cambiar el estado
    @action(detail=True, methods=['patch'])
    def cambiar_estado(self, request, pk=None):
        try:
            usuario = self.get_object()
            nuevo_estado = 'Activo' if usuario.estado == 'Inactivo' else 'Inactivo'
            usuario.estado = nuevo_estado
            usuario.save()
            
            try:
                cliente = Cliente.objects.get(usuario_id = usuario)
                cliente.estado = nuevo_estado
                cliente.save()
            except Cliente.DoesNotExist:
                pass
            
            try:
                manicurista = Manicurista.objects.get(usuario_id = usuario)
                manicurista.estado = nuevo_estado
                manicurista.save()
            except Manicurista.DoesNotExist:
                pass
            
            serializer = self.get_serializer(usuario)
            return Response({
                'message':f'Estado del usuario cambiado a {nuevo_estado} y sus asociados',
                'data': serializer.data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'message':f'Ocurrio un error {str(e)}'},status=status.HTTP_500_INTERNAL_SERVER_ERROR)   
        
         
    # Filtrar usuarios por estado
    @action(detail=False, methods=['get'])
    def activos(self, request):
        usuarios_activos = Usuario.objects.filter(estado="Activo")
        serializer = self.get_serializer(usuarios_activos, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def inactivos(self, request):
        usuarios_inactivos = Usuario.objects.filter(estado="Inactivo")
        serializer = self.get_serializer(usuarios_inactivos, many=True)
        return Response(serializer.data)
    
    # Filtrar usuarios por rol
    @action(detail=False, methods=['get'])
    def por_rol(self, request):
        rol_id = request.query_params.get('rol_id', None)
        if rol_id:
            usuarios = Usuario.objects.filter(rol_id=rol_id)
            serializer = self.get_serializer(usuarios, many=True)
            return Response(serializer.data)
        return Response({"error": "Debe especificar un rol_id"}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def admin_recepcionista(self,request):
        try:
            roles_admin_recepcionista = Rol.objects.filter(nombre__in=['Administrador','Recepcionista']).values_list('id',flat=True)
            
            usuarios = Usuario.objects.filter(rol_id__in=roles_admin_recepcionista)
            
            serializer= self.get_serializer(usuarios, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'message': f'Ocurrió un error: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)