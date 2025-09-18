from rest_framework import serializers
from django.db import models
from datetime import date,time

import requests;

from proveedor.models import Proveedor
from ..models.compra import Compra
from ..models.estado_compra import EstadoCompra

class ComprasSerializer(serializers.ModelSerializer):
    estadoCompra_id = serializers.PrimaryKeyRelatedField(queryset= EstadoCompra.objects.all())
    
    proveedor_id = serializers.PrimaryKeyRelatedField(queryset=Proveedor.objects.all())
    
    estado_nombre = serializers.SerializerMethodField()
    
    observacion = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    
    class Meta:
        model = Compra
        fields = [
            'id',
            'proveedor_id',
            'estadoCompra_id',
            'estado_nombre',
            'fechaIngreso',
            'fechaCompra',
            'total',
            'IVA',
            'observacion', 
        ]
        
    def get_estado_nombre(self,obj):
        return obj.estadoCompra_id.Estado
    
    def validate(self,data):
        if 'fechaIngreso' in data and 'fechaCompra' in data:
            if data['fechaIngreso'] < data['fechaCompra']:
                raise serializers.ValidationError("La fecha de ingreso no debe ser menor a la fecha de compra")
        return data
    
    