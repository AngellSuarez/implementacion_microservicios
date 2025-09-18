from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from django.contrib.auth.hashers import make_password
from usuario.models.usuario_model import Usuario
from random import randint
from datetime import timedelta

from ..models import CodigoRecuperacion
from utils.email_utils import enviar_correo_recuperacion

class SolicitarCodigoRecuperacionView(APIView):
    def post(self, request):
        correo = request.data.get('correo')

        if not correo:
            return Response({"error": "Debe proporcionar un correo."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            usuario = Usuario.objects.get(correo=correo)
        except Usuario.DoesNotExist:
            return Response({"error": "No se encontró un usuario con ese correo."}, status=status.HTTP_404_NOT_FOUND)

        # Generar código de 6 dígitos
        codigo = f"{randint(100000, 999999)}"
        expiracion = timezone.now() + timedelta(minutes=10)

        # Guardar o actualizar el código en la tabla
        CodigoRecuperacion.objects.update_or_create(
            usuario=usuario,
            defaults={
                'codigo': codigo,
                'creado_en': timezone.now(),
                'expiracion': expiracion
            }
        )

        asunto = "Código de recuperación de contraseña"


        if enviar_correo_recuperacion(correo, asunto, codigo):
            return Response({"mensaje": "Código enviado al correo."}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Error al enviar el correo."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)