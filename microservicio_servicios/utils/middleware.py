# microservicio_servicios/utils/auth_middleware.py
import requests
import logging
from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.core.cache import cache
from rest_framework_simplejwt.exceptions import InvalidToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import UntypedToken
from jwt import decode as jwt_decode
from django.contrib.auth import get_user_model

logger = logging.getLogger(__name__)

# URL del monolítico
MONOLITH_URL = getattr(settings, 'MONOLITH_URL', 'http://localhost:8000/api')

class ProxyUser:
    """Clase que simula un usuario para el microservicio"""
    def __init__(self, user_data):
        self.id = user_data.get('id')
        self.username = user_data.get('username')
        self.email = user_data.get('correo', user_data.get('email', ''))
        self.nombre = user_data.get('nombre', '')
        self.apellido = user_data.get('apellido', '')
        self.rol_id = user_data.get('rol_id')
        self.estado = user_data.get('estado', 'Activo')
        self.is_authenticated = True
        self.is_active = user_data.get('estado') == 'Activo'
        self.is_staff = False
        self.is_superuser = False
        
    def __str__(self):
        return self.username

class MicroserviceJWTAuthentication(JWTAuthentication):
    """Autenticación JWT personalizada para microservicios"""
    
    def get_user(self, validated_token):
        """Obtiene datos del usuario desde el monolítico"""
        try:
            user_id = validated_token.get('user_id')
            if not user_id:
                return None
                
            # Verificar cache primero
            cache_key = f"user_data_{user_id}"
            user_data = cache.get(cache_key)
            
            if user_data is None:
                # Solicitar datos del usuario al monolítico
                user_data = self._fetch_user_from_monolith(user_id)
                if user_data:
                    # Cachear por 5 minutos
                    cache.set(cache_key, user_data, 300)
                else:
                    return None
            
            return ProxyUser(user_data)
            
        except Exception as e:
            logger.error(f"Error obteniendo usuario: {e}")
            return None
    
    def _fetch_user_from_monolith(self, user_id):
        """Obtiene datos del usuario desde el monolítico"""
        try:
            url = f"{MONOLITH_URL}/usuario/{user_id}/"
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 404:
                logger.warning(f"Usuario {user_id} no encontrado en monolítico")
                return None
            else:
                logger.error(f"Error HTTP {response.status_code} al obtener usuario {user_id}")
                return None
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Error de conexión con monolítico: {e}")
            return None
        except Exception as e:
            logger.error(f"Error inesperado: {e}")
            return None

# microservicio_servicios/utils/auth_utils.py
def verificar_token_con_monolitico(token):
    """Verifica un token JWT directamente con el monolítico"""
    try:
        headers = {'Authorization': f'Bearer {token}'}
        url = f"{MONOLITH_URL}/auth/verify-token/"
        
        response = requests.post(url, headers=headers, timeout=5)
        
        if response.status_code == 200:
            return response.json()
        return None
        
    except Exception as e:
        logger.error(f"Error verificando token: {e}")
        return None