import requests
import logging
from rest_framework.permissions import BasePermission
from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger(__name__)

# URL de tu microservicio de roles/autenticación
AUTH_MS_URL = getattr(settings, 'AUTH_MS_URL', "http://localhost:8000/api/rol/")

def obtener_permisos_usuario(usuario_id, rol_id):
    """Obtiene los módulos permitidos para un usuario a través de la API."""
    if getattr(settings, 'MIGRATING', False):
        return []
    
    cache_key = f"modulos_rol_{rol_id}"
    modulos = cache.get(cache_key)
    if modulos is not None:
        logger.debug(f"Módulos obtenidos desde cache para rol {rol_id}")
        return modulos
    
    try:
        url = f"{AUTH_MS_URL}permisos-rol/modulos-por-rol/?rol_id={rol_id}/"
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        
        data = response.json()
        modulos = data.get('modulos', [])
        
        cache.set(cache_key, modulos, 300)  # cache 5 minutos
        logger.info(f"Módulos obtenidos para rol {rol_id}: {modulos}")
        return modulos
    except requests.exceptions.RequestException as e:
        logger.error(f"Error de conexión con microservicio de roles: {e}")
        return []
    except Exception as e:
        logger.error(f"Error inesperado: {e}")
        return []


def TienePermisoModulo(modulo_requerido):
    """
    Verificador de permisos por módulo - devuelve el permiso ya instanciado
    """
    class _PermisoModulo(BasePermission):
        def has_permission(self, request, view):
            # Permitir métodos de solo lectura
            if request.method in ('GET', 'HEAD', 'OPTIONS'):
                return True

            # Verificar autenticación
            if not request.user.is_authenticated:
                return False

            # Verificar rol
            if not hasattr(request.user, 'rol_id') or not request.user.rol_id:
                logger.warning(f"Usuario {getattr(request.user, 'id', None)} sin rol asignado")
                return False

            # Cache a nivel de request
            if not hasattr(request.user, 'modulos_cache'):
                request.user.modulos_cache = obtener_permisos_usuario(
                    request.user.id,
                    request.user.rol_id
                )

            tiene_permiso = modulo_requerido in request.user.modulos_cache

            if not tiene_permiso:
                logger.info(
                    f"Usuario {request.user.id} (rol {request.user.rol_id}) "
                    f"NO tiene acceso a módulo '{modulo_requerido}'. "
                    f"Módulos disponibles: {request.user.modulos_cache}"
                )
            
            return tiene_permiso
    
    return _PermisoModulo()  # ← ya devuelve el permiso instanciado ✅


# -------------------- Utilidades --------------------

def limpiar_cache_permisos(rol_id=None):
    """Limpia el cache de permisos"""
    if rol_id:
        cache.delete(f"modulos_rol_{rol_id}")
    else:
        pattern = "modulos_rol_*"
        keys = cache.keys(pattern) if hasattr(cache, 'keys') else []
        if keys:
            cache.delete_many(keys)


def verificar_permiso_directo(usuario, modulo):
    """Verificación directa de permiso sin usar el decorador."""
    if not usuario.is_authenticated:
        return False
    
    if not hasattr(usuario, 'rol_id') or not usuario.rol_id:
        return False
    
    modulos = obtener_permisos_usuario(usuario.id, usuario.rol_id)
    return modulo in modulos


def debug_permisos_usuario(usuario):
    """Función de debug para ver todos los permisos de un usuario"""
    if not hasattr(usuario, 'rol_id') or not usuario.rol_id:
        return {"error": "Usuario sin rol"}
    
    modulos = obtener_permisos_usuario(usuario.id, usuario.rol_id)
    
    return {
        "usuario_id": usuario.id,
        "rol_id": usuario.rol_id,
        "modulos_permitidos": modulos,
        "total_modulos": len(modulos)
    }
