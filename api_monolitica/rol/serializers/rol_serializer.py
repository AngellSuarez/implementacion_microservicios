from rest_framework import serializers;
from ..models import Rol;

class RolSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rol;
        fields = '__all__';
        
        def validate_nombre(self, nombre):
            if not nombre:
                raise serializers.ValidationError("El nombre no puede estar vacio");
            if len(nombre) <3:
                raise serializers.ValidationError("El nombre debe tener al menos 3 caracteres");
            if nombre.isdigit():
                raise serializers.ValidationError("El nombre no puede ser solo numeros");
            return nombre;
        
        def validate_descripcion(self, descripcion):
            if len(descripcion) <3:
                raise serializers.ValidationError("La descripcion debe tener al menos 3 caracteres");
            if descripcion.isdigit():
                raise serializers.ValidationError("La descripcion no puede ser solo numeros");
            return descripcion;
        
        def validate_estado(self, estado):
            if not estado:
                raise serializers.ValidationError("El estado no puede estar vacio");
            return estado;