from rest_framework.permissions import BasePermission

from rol.models import Permiso_Rol


def obtener_permisos_usuario(usuario):
   """
   Obtiene los permisos de un usuario, devolviendo una lista con los modulos (permisos) que tiene el rol asignado."""
  
   if not usuario.rol_id:
       return []
  
   permisos = Permiso_Rol.objects.filter(rol_id=usuario.rol_id).select_related("permiso_id")
   modulos = [p.permiso_id.modulo for p in permisos if p.permiso_id and p.permiso_id.modulo]
   return modulos


def TienePermisoModulo(modulo_requerido):
    class _PermisoModulo(BasePermission):
        def has_permission(self, request, view):
            if request.method in ('GET', 'HEAD', 'OPTIONS'):
                return True  # Permitir libremente métodos de solo lectura

            usuario = request.user
            if not usuario.is_authenticated:
                return False

            permisos = getattr(usuario, 'permisos_cache', None)
            if permisos is None:
                permisos = obtener_permisos_usuario(usuario)
                usuario.permisos_cache = permisos

            return modulo_requerido in permisos
    return _PermisoModulo
