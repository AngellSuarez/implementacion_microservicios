from rest_framework import serializers
from django.db import models

from insumo.models import Insumo
from ..models.compra_insumo import CompraInsumo
from ..models.compra import Compra

class CompraInsumoSerializer(serializers.ModelSerializer):

    class Meta:
        model = CompraInsumo
        fields = '__all__'

    def validate_compra_id(self, compra_id):
        try:
            Compra.objects.get(id=compra_id.id)
        except Compra.DoesNotExist:
            raise serializers.ValidationError("La compra no existe")
        if not compra_id:
            raise serializers.ValidationError("La compra es requerida")
        return compra_id

    def validate_insumo_id(self, insumo_id):
        try:
            insumo_buscado = Insumo.objects.get(id=insumo_id.id)
        except Insumo.DoesNotExist:
            raise serializers.ValidationError("El insumo no existe")
        if not insumo_id:
            raise serializers.ValidationError("El insumo es necesario")
        if insumo_buscado.estado == "inactivo":
            raise serializers.ValidationError("El insumo debe estar activo")
        return insumo_id

    def validate_cantidad(self, cantidad):
        if cantidad < 0:
            raise serializers.ValidationError("La cantidad no puede ser negativa")
        if cantidad == 0:
            raise serializers.ValidationError("La cantidad no puede ser 0")
        return cantidad

    def validate_precioUnitario(self, precioUnitario):
        if precioUnitario is not None and precioUnitario < 0:
            raise serializers.ValidationError("El precio unitario no puede ser negativo")
        return precioUnitario

    def validate_subtotal(self, subtotal):
        # El subtotal se calculará automáticamente, así que no necesitamos validarlo aquí
        return subtotal

    def validate(self, data):
        if 'compra_id' in data and 'insumo_id' in data:
            query_existente = CompraInsumo.objects.filter(
                compra_id=data['compra_id'],
                insumo_id=data['insumo_id']
            )
            if self.instance:
                query_existente = query_existente.exclude(id=self.instance.id)
            if query_existente.exists():
                raise serializers.ValidationError({
                    'non_fields_errors': "El insumo ya se encuentra dentro de la compra"
                })
        return data

    def create(self, validated_data):
        validated_data['subtotal'] = validated_data['cantidad'] * validated_data.get('precioUnitario', 0)
        compra_insumo = super().create(validated_data)
        self._actualizar_total_compra(compra_insumo.compra_id)
        return compra_insumo

    def update(self, instance, validated_data):
        validated_data['subtotal'] = validated_data.get('cantidad', instance.cantidad) * validated_data.get('precioUnitario', instance.precioUnitario)
        compra_insumo = super().update(instance, validated_data)
        self._actualizar_total_compra(compra_insumo.compra_id)
        return compra_insumo

    def _actualizar_total_compra(self, compra):
        total_subtotales = CompraInsumo.objects.filter(compra_id=compra).aggregate(
            total_subtotales=models.Sum('subtotal')
        )['total_subtotales'] or 0

        iva = compra.IVA  
        total_con_iva = total_subtotales + (total_subtotales * iva)

        compra.total = total_con_iva
        compra.save()