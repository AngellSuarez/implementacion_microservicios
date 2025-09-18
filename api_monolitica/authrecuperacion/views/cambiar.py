from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from usuario.models.usuario_model import Usuario

@api_view(['POST'])
def cambiar_password(request):
    correo = request.data.get('correo')
    nueva_password = request.data.get('nueva_password')

    if not correo or not nueva_password:
        return Response({'error': 'Correo y nueva contraseña son obligatorios.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        usuario = Usuario.objects.get(correo=correo)
        usuario.set_password(nueva_password)
        usuario.save()
        return Response({'message': 'Contraseña actualizada exitosamente.'}, status=status.HTTP_200_OK)
    except Usuario.DoesNotExist:
        return Response({'error': 'Usuario no encontrado.'}, status=status.HTTP_404_NOT_FOUND)
