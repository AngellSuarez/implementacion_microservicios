from rest_framework import serializers
from django.db import models
from datetime import date, time
import requests;

# from servicio.models import Servicio 
from ..models.cita_venta_model import CitaVenta
from ..models.servicio_cita_model import ServicioCita
SERVICIO_MS_URL = "http://localhost:8001/api/servicios/"

class ServicioCitaSerializer(serializers.ModelSerializer):
    servicio_nombre = serializers.CharField(source='servicio_id.nombre', read_only=True)
    class Meta:
        model = ServicioCita
        fields = ('id', 'cita_id', 'servicio_id', 'subtotal', 'servicio_nombre')

    def validate_cita_id(self, cita_id):
        try:
            CitaVenta.objects.get(id=cita_id.id)
        except CitaVenta.DoesNotExist:
            raise serializers.ValidationError("La cita no existe")
        return cita_id

    def validate_servicio_id(self, servicio_id):
        try:
            response = requests.get(f"{SERVICIO_MS_URL}{servicio_id.id}/")
            if response.status_code != 200:
                raise serializers.ValidationError("El servicio no existe o no está disponible.")
            servicio_data = response.json()
            self.servicio_precio = servicio_data.get('precio', 0)
        except requests.exceptions.RequestException:
            raise serializers.ValidationError("No se pudo conectar con el microservicio de servicios.")
        return servicio_id

    def validate_subtotal(self, subtotal):
        if subtotal < 0:
            raise serializers.ValidationError("El subtotal no puede ser negativo")
        return subtotal

    def validate(self, data):   
        #lógica de negocio centralizada
        if 'cita_id' in data and 'servicio_id' in data:
            query_existente = ServicioCita.objects.filter(
                cita_id=data['cita_id'],
                servicio_id=data['servicio_id'],
            )
            if self.instance:
                query_existente = query_existente.exclude(id=self.instance.id)
            if query_existente.exists():
                raise serializers.ValidationError({
                    "non_field_errors": "El servicio ya se encuentra registrado en la cita"
                })
        
        # Uso del precio obtenido en validate_servicio_id
        if not self.instance and 'subtotal' not in data:
            data['subtotal'] = self.servicio_precio
            
        return data

    def create(self, validated_data):
        servicioCita = super().create(validated_data)
        self._actualizar_total_cita(servicioCita.cita_id)
        return servicioCita
        
    def update(self, instance, validated_data):
        servicioCita = super().update(instance, validated_data)
        self._actualizar_total_cita(servicioCita.cita_id)
        return servicioCita
        
    def _actualizar_total_cita(self, cita):
        nuevo_total = ServicioCita.objects.filter(cita_id=cita).aggregate(
            total=models.Sum('subtotal')
        )['total'] or 0
        cita.Total = nuevo_total
        cita.save()