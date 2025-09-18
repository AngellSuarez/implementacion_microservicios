from rest_framework import serializers
from django.db import transaction
from ..models.abastecimiento import Abastecimiento
from ..models.insumoAbastecimiento import InsumoAbastecimiento
from usuario.models.manicurista_model import Manicurista
from insumo.models import Insumo

class InsumoAbastecimientoSerializer(serializers.ModelSerializer):
    insumo_nombre = serializers.CharField(source='insumo_id.nombre', read_only=True)
    insumo_stock = serializers.IntegerField(source='insumo_id.stock', read_only=True)
    abastecimiento_fecha = serializers.DateField(source='abastecimiento_id.fecha_creacion', read_only=True)
    
    class Meta:
        model = InsumoAbastecimiento
        fields = ['id', 'insumo_id', 'insumo_nombre', 'insumo_stock', 
                 'abastecimiento_id', 'abastecimiento_fecha', 'cantidad', 
                 'estado', 'comentario']

    def validate_cantidad(self, value):
        if value < 1:
            raise serializers.ValidationError("La cantidad debe ser mayor a 0.")
        return value

    def validate(self, attrs):
        insumo = attrs.get('insumo_id')
        cantidad = attrs.get('cantidad')
        
        if insumo and cantidad:
            if insumo.stock < cantidad:
                raise serializers.ValidationError({
                    'cantidad': f'No hay suficiente stock. Stock disponible: {insumo.stock}'
                })
        
        return super().validate(attrs)

    @transaction.atomic
    def create(self, validated_data):
        insumo = validated_data['insumo_id']
        cantidad = validated_data['cantidad']
        
        # Restar la cantidad del stock del insumo
        insumo.stock -= cantidad
        insumo.save()
        
        # Crear el registro de InsumoAbastecimiento
        insumo_abastecimiento = super().create(validated_data)
        
        return insumo_abastecimiento

    @transaction.atomic
    def update(self, instance, validated_data):
        # Si se está actualizando la cantidad, ajustar el stock
        if 'cantidad' in validated_data:
            cantidad_anterior = instance.cantidad
            cantidad_nueva = validated_data['cantidad']
            diferencia = cantidad_nueva - cantidad_anterior
            
            insumo = instance.insumo_id
            
            # Validar que hay suficiente stock para el incremento
            if diferencia > 0 and insumo.stock < diferencia:
                raise serializers.ValidationError({
                    'cantidad': f'No hay suficiente stock para aumentar la cantidad. Stock disponible: {insumo.stock}'
                })
            
            # Ajustar el stock
            insumo.stock -= diferencia
            insumo.save()
        
        return super().update(instance, validated_data)