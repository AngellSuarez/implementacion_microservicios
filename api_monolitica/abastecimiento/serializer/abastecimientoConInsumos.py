from rest_framework import serializers
from ..models.abastecimiento import Abastecimiento
from ..models.insumoAbastecimiento import InsumoAbastecimiento
from usuario.models.manicurista_model import Manicurista
from insumo.models import Insumo
from .insumoAbastecimientoSerializer import InsumoAbastecimientoSerializer

class AbastecimientoConInsumosSerializer(serializers.ModelSerializer):
    insumos = InsumoAbastecimientoSerializer(source='insumoabastecimiento_set', many=True, read_only=True)
    manicurista_nombre = serializers.SerializerMethodField()
    total_insumos = serializers.SerializerMethodField()
    
    class Meta:
        model = Abastecimiento
        fields = ['id', 'fecha_creacion', 'manicurista_id', 'manicurista_nombre',
                 'estado', 'fecha_reporte', 'insumos', 'total_insumos']
        read_only_fields = ['fecha_reporte']
    
    def get_total_insumos(self, obj):
        return obj.insumoabastecimiento_set.count()
    
    def get_manicurista_nombre(self, obj):
        return f"{obj.manicurista_id.nombre} {obj.manicurista_id.apellido}"
