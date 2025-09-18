from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from django.contrib.auth.hashers import make_password
from usuario.models.usuario_model import Usuario
from random import randint
from datetime import timedelta

from ..models import CodigoRecuperacion
from utils.email_utils import enviar_correo_cambio_password

class ConfirmarCodigoRecuperacionView(APIView):
    def post(self, request):
        correo = request.data.get('correo')
        codigo = request.data.get('codigo')
        nueva_password = request.data.get('nueva_password')

        if not all([correo, codigo, nueva_password]):
            return Response({"error": "Faltan datos requeridos."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            usuario = Usuario.objects.get(correo=correo)
            codigo_obj = CodigoRecuperacion.objects.get(usuario=usuario, codigo=codigo)
        except (Usuario.DoesNotExist, CodigoRecuperacion.DoesNotExist):
            return Response({"error": "Código inválido o usuario no encontrado."}, status=status.HTTP_400_BAD_REQUEST)

        if codigo_obj.expiracion < timezone.now():
            return Response({"error": "El código ha expirado."}, status=status.HTTP_400_BAD_REQUEST)

        # Actualizar la contraseña
        usuario.set_password(nueva_password)
        usuario.save()

        # Eliminar el código
        codigo_obj.delete()
        enviar_correo_cambio_password(usuario.correo, usuario.nombre)


        return Response({"mensaje": "Contraseña actualizada correctamente."}, status=status.HTTP_200_OK)