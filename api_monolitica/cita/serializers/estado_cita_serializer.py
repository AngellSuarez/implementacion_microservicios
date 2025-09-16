from rest_framework import serializers
from ..models.estado_cita_model import EstadoCita
from django.db import models

class EstadoCitaSerializer(serializers.ModelSerializer):
    class Meta:
        model = EstadoCita
        fields = '__all__'
        
    def validate_Estado(self, Estado):
        if not Estado:
            raise serializers.ValidationError("El estado es requerido")
        if len(Estado) < 3:
            raise serializers.ValidationError("El estado debe tener al menos 3 caracteres")
        if Estado.isdigit():
            raise serializers.ValidationError("El estado no puede contener solo numeros")
        return Estado