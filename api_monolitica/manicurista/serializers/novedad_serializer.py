from rest_framework import serializers
from datetime import date, time, timedelta
from django.db import models
from ..models.novedades_model import Novedades
from usuario.models.manicurista_model import Manicurista

class NovedadesSerializer(serializers.ModelSerializer):
    manicurista_id = serializers.PrimaryKeyRelatedField(queryset=Manicurista.objects.all())
    manicurista_nombre = serializers.SerializerMethodField()

    class Meta:
        model = Novedades
        fields = [
            'id',
            'manicurista_id',
            'Fecha',
            'HoraEntrada',
            'HoraSalida',
            'Motivo',
            'manicurista_nombre',
        ]

    def get_manicurista_nombre(self, obj):
        return f"{obj.manicurista_id.nombre} {obj.manicurista_id.apellido}"

    def validate_Fecha(self, value):
        max_fecha = date.today() + timedelta(days=7)
        if value > max_fecha:
            raise serializers.ValidationError("La fecha no puede superar 7 días desde hoy.")
        return value

    def validate_HoraEntrada(self, value):
        if value < time(8, 0) or value > time(18, 0):
            raise serializers.ValidationError("La hora de entrada debe estar entre las 8:00 AM y las 6:00 PM.")
        return value

    def validate_HoraSalida(self, value):
        if value < time(8, 0) or value > time(18, 0):
            raise serializers.ValidationError("La hora de salida debe estar entre las 8:00 AM y las 6:00 PM.")
        return value

    def validate(self, data):
        hora_entrada = data.get("HoraEntrada")
        hora_salida = data.get("HoraSalida")
        manicurista_id = data.get("manicurista_id")
        fecha = data.get("Fecha")
        
        # Validar que la hora de salida sea posterior a la hora de entrada
        if hora_entrada and hora_salida and hora_salida <= hora_entrada:
            raise serializers.ValidationError("La hora de salida debe ser posterior a la hora de entrada.")
        
        if manicurista_id and fecha and hora_entrada and hora_salida:
            # Obtener novedades existentes para la misma manicurista y fecha
            existing_novedades = Novedades.objects.filter(
                manicurista_id=manicurista_id,
                Fecha=fecha
            )
        
            if self.instance:
                existing_novedades = existing_novedades.exclude(id=self.instance.id)
            
            # Verificar solapamientos
            for novedad_existente in existing_novedades:
                entrada_existente = novedad_existente.HoraEntrada
                salida_existente = novedad_existente.HoraSalida
                
                # Verificar si hay solapamiento
                # Caso 1: La nueva entrada está dentro de un horario existente
                if entrada_existente <= hora_entrada < salida_existente:
                    raise serializers.ValidationError(
                        f"La hora de entrada ({hora_entrada.strftime('%H:%M')}) se solapa con una novedad existente "
                        f"({entrada_existente.strftime('%H:%M')} - {salida_existente.strftime('%H:%M')})."
                    )
                
                # Caso 2: La nueva salida está dentro de un horario existente
                if entrada_existente < hora_salida <= salida_existente:
                    raise serializers.ValidationError(
                        f"La hora de salida ({hora_salida.strftime('%H:%M')}) se solapa con una novedad existente "
                        f"({entrada_existente.strftime('%H:%M')} - {salida_existente.strftime('%H:%M')})."
                    )
                
                # Caso 3: El nuevo horario engloba completamente uno existente
                if hora_entrada <= entrada_existente and hora_salida >= salida_existente:
                    raise serializers.ValidationError(
                        f"El horario propuesto ({hora_entrada.strftime('%H:%M')} - {hora_salida.strftime('%H:%M')}) "
                        f"engloba una novedad existente ({entrada_existente.strftime('%H:%M')} - {salida_existente.strftime('%H:%M')})."
                    )
                
                # Caso 4: Un horario existente engloba completamente el nuevo
                if entrada_existente <= hora_entrada and salida_existente >= hora_salida:
                    raise serializers.ValidationError(
                        f"Ya existe una novedad que cubre este horario "
                        f"({entrada_existente.strftime('%H:%M')} - {salida_existente.strftime('%H:%M')})."
                    )
            
            # Verificar si ya existe una novedad de día completo (8:00 AM - 6:00 PM)
            novedad_completa = existing_novedades.filter(
                HoraEntrada=time(8, 0),
                HoraSalida=time(18, 0)
            ).first()
            
            if novedad_completa:
                raise serializers.ValidationError(
                    "Ya existe una novedad para todo el día (8:00 AM - 6:00 PM). "
                    "No se pueden crear más novedades para esta fecha."
                )
        
        return data