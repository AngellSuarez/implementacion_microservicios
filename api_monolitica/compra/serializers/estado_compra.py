from rest_framework import serializers
from ..models.estado_compra import EstadoCompra
from django.db import models

class EstadoCompraSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = EstadoCompra
        fields = '__all__'
        
    def validate_Estado(self, Estado):
        if not Estado:
            raise serializers.ValidationError("El estado es necesario")
        if len(Estado) < 3:
            raise serializers.ValidationError("El estado debe tener mas de 3 letras")
        if Estado.isdigit():
            raise serializers.ValidationError("El estado no pueden ser solo números")
        return Estado