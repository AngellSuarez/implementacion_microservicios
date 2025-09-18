from rest_framework import serializers
from ..models.abastecimiento import Abastecimiento
from ..models.insumoAbastecimiento import InsumoAbastecimiento
from usuario.models.manicurista_model import Manicurista
from insumo.models import Insumo

class AbastecimientoSerializer(serializers.ModelSerializer):
    manicurista_id = serializers.PrimaryKeyRelatedField(queryset=Manicurista.objects.all())
    
    manicurista_nombre = serializers.SerializerMethodField()
    
    class Meta:
        model = Abastecimiento
        fields = ['id', 'fecha_creacion', 'manicurista_id', 'estado', 'fecha_reporte', 'manicurista_nombre']
        read_only_fields = ['fecha_creacion', 'estado', 'fecha_reporte']
        
    def get_manicurista_nombre(self, obj):
        return f"{obj.manicurista_id.nombre} {obj.manicurista_id.apellido}"

    def validate_manicurista_id(self, value):
        if not Manicurista.objects.filter(usuario_id=value.usuario_id).exists():
            raise serializers.ValidationError("El manicurista especificado no existe.")
        return value
    
    def validate(self,data):
        if Abastecimiento.objects.filter(manicurista_id=data['manicurista_id'], estado='Sin reportar').exists():
            raise serializers.ValidationError("Ya existe un abastecimiento pendiente para este manicurista.")
        return data