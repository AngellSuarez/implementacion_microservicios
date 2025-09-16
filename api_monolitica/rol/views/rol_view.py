from rest_framework import viewsets, status, permissions;
from rest_framework.response import Response;
from rest_framework.decorators import action;
from rest_framework.permissions import AllowAny;

from ..models import Rol
from ..models import Permiso_Rol
from ..serializers.rol_serializer import RolSerializer
from usuario.models.usuario_model import Usuario
from usuario.models.manicurista_model import Manicurista
from usuario.models.cliente_model import Cliente

from utils.permisos import TienePermisoModulo

#@verificar_permiso('rol')
class RolViewSet(viewsets.ModelViewSet):
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        old_estado = instance.estado
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        # Si el estado cambió, actualizar usuarios, manicuristas y clientes vinculados
        new_estado = serializer.instance.estado
        if 'estado' in request.data and old_estado != new_estado:
            usuarios = Usuario.objects.filter(rol_id=instance.id)
            usuarios.update(estado=new_estado)
            # Actualizar manicuristas vinculados
            manicuristas = Manicurista.objects.filter(usuario__in=usuarios)
            manicuristas.update(estado=new_estado)
            # Actualizar clientes vinculados
            clientes = Cliente.objects.filter(usuario__in=usuarios)
            clientes.update(estado=new_estado)
        return Response(serializer.data)
    queryset = Rol.objects.all();
    serializer_class = RolSerializer;
    permission_classes = [TienePermisoModulo("Rol")];
    
    #detalles con servicios
    @action(detail=True, methods=['get'])
    def detalle_con_permiso(self,request,pk=None):
        rol = self.get_object()
        
        #obtener los permisos
        permiso_rol = Permiso_Rol.objects.filter(rol_id = rol.id).select_related("permiso_id")
        
        permiso_serializado = [
            {
                "id":pr.permiso_id.id,
                "modulo":pr.permiso_id.modulo,
            }
            for pr in permiso_rol
        ]
        
        data = {
            "rol": {
                "id": rol.id,
                "nombre": rol.nombre,
                "descripcion": rol.descripcion,
                "estado": rol.estado
            },
            "modulos":permiso_serializado
        }
        
        return Response(data)
    
    #cambiar estado
    @action(detail=True, methods=['patch'])
    def cambiar_estado(self, request, pk=None):
        rol = self.get_object()
        nuevo_estado = "Activo" if rol.estado == "Inactivo" else "Inactivo"
        rol.estado = nuevo_estado
        rol.save()
        
    #encontrar usuarios activos
        usuarios = Usuario.objects.filter(rol_id=rol.id)
        usuarios.update(estado=nuevo_estado)
        for usuario in usuarios:
            # Si el usuario tiene un manicurista asociado, desactívalo
            if hasattr(usuario, 'manicurista'):
                manicurista = usuario.manicurista
                if manicurista:
                    manicurista.estado = nuevo_estado
                    manicurista.save()
            # Si el usuario tiene un cliente asociado, desactívalo
            if hasattr(usuario, 'cliente'):
                cliente = usuario.cliente
                if cliente:
                    cliente.estado = nuevo_estado
                    cliente.save()
        serializer = self.get_serializer(rol)
        return Response({
            "message": f"El estado del rol cambió a {nuevo_estado} correctamente",
            "data": serializer.data
    })
    
    #cambiar el eliminar (destroy en django para inactivo)
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object();

        usuarios_activos = Usuario.objects.filter(rol_id=instance, estado="Activo").exists()
        
        if usuarios_activos:
            instance.estado = "Inactivo"
            instance.save()
            usuarios_activo = Usuario.objects.filter(rol_id=instance).update(estado="Inactivo")
            return Response(
                {"message":"El rol tiene usuarios activos, por lo que se ha desactivado"}, status = status.HTTP_200_OK
            )
        else:
            instance.delete()
            usuarios_activos.delete()
            return Response({
                "message":"El rol no cuenta con usuarios activos, por lo cual se elimino"
            },status=status.HTTP_204_NO_CONTENT)
    
    #filtrar roles por estado
    @action(detail=False,methods=['get'])
    def activos(self,request):
        roles_activos = Rol.objects.filter(estado="Activo");
        serializer = self.get_serializer(roles_activos, many=True);
        return Response(serializer.data);
    
    @action(detail=False,methods=["get"])
    def inactivos(self,request):
        roles_inactivos = Rol.objects.filter(estado="Inactivo");
        serializer = self.get_serializer(roles_inactivos, many=True);
        return Response(serializer.data);