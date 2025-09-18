from rest_framework import serializers
from ..models import CodigoRecuperacion
from usuario.models.usuario_model import Usuario

class SolicitudCodigoSerializer(serializers.Serializer):
    correo = serializers.EmailField()
    
    def validate_correo(self,value):
        if not Usuario.objects.filter(correo=value).exists():
            raise serializers.ValidationError("No existe un usuario con ese correo")
        return value