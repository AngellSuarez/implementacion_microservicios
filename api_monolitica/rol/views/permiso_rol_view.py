from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny

from ..models import Permiso_Rol
from ..serializers import PermisoRolSerializer

class PermisoRolViewSet(viewsets.ModelViewSet):
    queryset = Permiso_Rol.objects.all()
    serializer_class = PermisoRolSerializer
    permission_classes = [AllowAny]
    
    @action(detail=False, methods=['get'])
    def permisos_por_rol(self, request):
        """
        Endpoint principal que devuelve módulos y detalles completos
        """
        rol_id = request.query_params.get('rol_id')
        if not rol_id:
            return Response({
                "error": "Debe especificar un rol_id"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Consulta optimizada con select_related
            permisos_roles = Permiso_Rol.objects.filter(
                rol_id=rol_id
            ).select_related('permiso_id', 'rol_id')
            
            # Extraer módulos únicos
            modulos = list(set(
                pr.permiso_id.modulo 
                for pr in permisos_roles 
                if pr.permiso_id and pr.permiso_id.modulo
            ))
            
            # Crear detalles
            permisos_detalle = []
            for permiso_rol in permisos_roles:
                if permiso_rol.permiso_id:
                    permisos_detalle.append({
                        'id': permiso_rol.id,
                        'rol_id': permiso_rol.rol_id.id if permiso_rol.rol_id else None,
                        'rol_nombre': permiso_rol.rol_id.nombre if permiso_rol.rol_id else None,
                        'permiso_id': permiso_rol.permiso_id.id,
                        'modulo': permiso_rol.permiso_id.modulo
                    })
            
            return Response({
                'rol_id': int(rol_id),
                'modulos': modulos,
                'permisos_detalle': permisos_detalle,
                'total_permisos': len(permisos_detalle)
            })
            
        except Exception as e:
            return Response({
                "error": f"Error al obtener permisos: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'], url_path='modulos-por-rol')
    def modulos_por_rol(self, request):
        """
        Endpoint súper optimizado solo para módulos (ideal para microservicios)
        """
        rol_id = request.query_params.get('rol_id')
        if not rol_id:
            return Response({
                "error": "Debe especificar un rol_id"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Una sola consulta optimizada que obtiene módulos únicos directamente
            modulos = list(
                Permiso_Rol.objects
                .filter(rol_id=rol_id)
                .select_related('permiso_id')
                .values_list('permiso_id__modulo', flat=True)
                .distinct()
            )
            
            # Filtrar valores None
            modulos = [m for m in modulos if m]
            
            return Response({
                'rol_id': int(rol_id),
                'modulos': modulos
            })
            
        except Exception as e:
            return Response({
                "error": f"Error al obtener módulos: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'])
    def roles_por_permiso(self, request):
        """
        Obtener todos los roles que tienen un permiso específico
        """
        permiso_id = request.query_params.get('permiso_id')
        if not permiso_id:
            return Response({
                "error": "Debe especificar un permiso_id"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        permisos_roles = Permiso_Rol.objects.filter(permiso_id=permiso_id)
        serializer = self.get_serializer(permisos_roles, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], url_path='roles-por-modulo')
    def roles_por_modulo(self, request):
        """
        Obtener todos los roles que tienen acceso a un módulo específico
        """
        modulo = request.query_params.get('modulo')
        if not modulo:
            return Response({
                "error": "Debe especificar un módulo"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            roles = list(
                Permiso_Rol.objects
                .filter(permiso_id__modulo=modulo)
                .select_related('rol_id')
                .values(
                    'rol_id__id', 
                    'rol_id__nombre', 
                    'rol_id__estado'
                )
                .distinct()
            )
            
            return Response({
                'modulo': modulo,
                'roles': roles,
                'total_roles': len(roles)
            })
            
        except Exception as e:
            return Response({
                "error": f"Error al obtener roles: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['post'], url_path='batch')
    def create_batch(self, request):
        """
        Crear múltiples relaciones permiso-rol de una vez
        """
        data = request.data
        if not isinstance(data, list):
            return Response({
                "error": "Se esperaba una lista de objetos"
            }, status=status.HTTP_400_BAD_REQUEST)

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