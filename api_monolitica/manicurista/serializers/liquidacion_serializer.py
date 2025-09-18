from rest_framework import serializers
from datetime import date, timedelta
from decimal import Decimal
from django.conf import settings
from django.core.mail import send_mail

from ..models.liquidacion_model import Liquidacion
from usuario.models.manicurista_model import Manicurista
from cita.models.cita_venta_model import CitaVenta
from utils.email_utils import enviar_correo_liquidacion_realizada  

class LiquidacionSerializer(serializers.ModelSerializer):
    manicurista_id = serializers.PrimaryKeyRelatedField(queryset=Manicurista.objects.all())
    manicurista_nombre = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Liquidacion
        fields = [
            'id',
            'manicurista_id',
            'FechaInicial',
            'FechaFinal',
            'TotalGenerado',
            'Comision',
            'Local',
            'manicurista_nombre',
        ]
        read_only_fields = ['TotalGenerado', 'Comision', 'Local', 'manicurista_nombre']

    def get_manicurista_nombre(self, obj):
        return f"{obj.manicurista_id.nombre} {obj.manicurista_id.apellido}"

    def validate_manicurista_id(self, manicurista_id):
        if not manicurista_id:
            raise serializers.ValidationError("El manicurista es requerido")
        return manicurista_id

    def validate(self, data):
        manicurista = data.get('manicurista_id')
        fecha_inicial = data.get('FechaInicial')
        fecha_final = data.get('FechaFinal')

        if not (manicurista and fecha_inicial and fecha_final):
            raise serializers.ValidationError("Debe proporcionar manicurista, fecha inicial y fecha final")

        if fecha_final != date.today():
            raise serializers.ValidationError({
                "FechaFinal": f"La fecha final debe ser hoy ({date.today()})"
            })

        if fecha_inicial != fecha_final - timedelta(days=5):
            raise serializers.ValidationError({
                "FechaInicial": f"La fecha inicial debe ser exactamente 5 días antes de la fecha final ({fecha_final - timedelta(days=5)})"
            })

        if Liquidacion.objects.filter(
            manicurista_id=manicurista,
            FechaInicial=fecha_inicial,
            FechaFinal=fecha_final
        ).exists():
            raise serializers.ValidationError("Ya existe una liquidación para este rango de fechas")

        return data

    def create(self, validated_data):
        manicurista = validated_data['manicurista_id']
        fecha_inicial = validated_data['FechaInicial']
        fecha_final = validated_data['FechaFinal']

        citas_venta = CitaVenta.objects.filter(
            manicurista_id=manicurista,
            Fecha__gte=fecha_inicial,
            Fecha__lte=fecha_final
        )

        total_generado = sum(cita.Total for cita in citas_venta)
        comision = total_generado * Decimal("0.5")
        local = total_generado * Decimal("0.5")

        validated_data['TotalGenerado'] = total_generado
        validated_data['Comision'] = comision
        validated_data['Local'] = local

        liquidacion = super().create(validated_data)

        destinatario = manicurista.correo  
        nombre_empleada = f"{manicurista.nombre} {manicurista.apellido}"
        enviar_correo_liquidacion_realizada(
            destinatario=destinatario,
            nombre_empleada=nombre_empleada,
            fecha_inicial=fecha_inicial,
            fecha_final=fecha_final,
            comision=comision
        )

        return liquidacion
