from rest_framework import serializers
from ..models import Permiso

class PermisoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permiso;
        fields = '__all__';
        
        def validate_modulo(self, modulo):
            if not modulo:
                raise serializers.ValidationError("El nombre no puede estar vacio");
            if len(modulo) <3:
                raise serializers.ValidationError("El nombre debe tener al menos 3 caracteres");
            if modulo.isdigit():
                raise serializers.ValidationError("El nombre no puede ser solo numeros");
            return modulo;