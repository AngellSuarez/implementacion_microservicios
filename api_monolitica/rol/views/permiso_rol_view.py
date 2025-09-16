from rest_framework import viewsets, status, permissions;
from rest_framework.response import Response;
from rest_framework.decorators import action;
from rest_framework.permissions import AllowAny;

from ..models import Permiso_Rol
from ..serializers import PermisoRolSerializer

class PermisoRolViewSet(viewsets.ModelViewSet):
    queryset = Permiso_Rol.objects.all()
    serializer_class = PermisoRolSerializer
    permission_classes = [AllowAny]
    
    # Obtener todos los permisos de un rol específico
    @action(detail=False, methods=['get'])
    def permisos_por_rol(self, request):
        rol_id = request.query_params.get('rol_id', None)
        if rol_id:
            permisos_roles = Permiso_Rol.objects.filter(rol_id=rol_id)
            serializer = self.get_serializer(permisos_roles, many=True)
            return Response(serializer.data)
        return Response({"error": "Debe especificar un rol_id"}, status=status.HTTP_400_BAD_REQUEST)
    
    # Obtener todos los roles con un permiso específico
    @action(detail=False, methods=['get'])
    def roles_por_permiso(self, request):
        permiso_id = request.query_params.get('permiso_id', None)
        if permiso_id:
            permisos_roles = Permiso_Rol.objects.filter(permiso_id=permiso_id)
            serializer = self.get_serializer(permisos_roles, many=True)
            return Response(serializer.data)
        return Response({"error": "Debe especificar un permiso_id"}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'], url_path='batch')
    def create_batch(self, request):
        data = request.data
        if not isinstance(data, list):
            return Response({"error": "Se esperaba una lista de objetos"},
                            status=status.HTTP_400_BAD_REQUEST)

        created_items = []
        errors = []
        permisos_roles = {}

        for entry in data:
            serializer = self.get_serializer(data=entry)
            if serializer.is_valid():
                permiso_rol = serializer.save()  

                rol = permiso_rol.rol_id
                permiso = permiso_rol.permiso_id

                if rol.id not in permisos_roles:
                    permisos_roles[rol.id] = {
                        "rol": rol.nombre,
                        "permisos": []
                    }

                permisos_roles[rol.id]["permisos"].append(permiso.modulo)

                created_items.append(serializer.data)
            else:
                errors.append(serializer.errors)

        return Response({
            "creados": created_items,
            "errores": errors,
            "asociaciones": permisos_roles
        }, status=status.HTTP_201_CREATED if not errors else status.HTTP_207_MULTI_STATUS)