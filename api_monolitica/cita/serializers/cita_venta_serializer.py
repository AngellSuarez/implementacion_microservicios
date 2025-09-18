from rest_framework import serializers
from datetime import datetime, timedelta
from django.utils import timezone
from usuario.models.manicurista_model import Manicurista
from usuario.models.cliente_model import Cliente
from manicurista.models.novedades_model import Novedades
from ..models.cita_venta_model import CitaVenta
from ..models.estado_cita_model import EstadoCita
from ..models.servicio_cita_model import ServicioCita

class CitaVentaSerializer(serializers.ModelSerializer):
    cliente_id = serializers.PrimaryKeyRelatedField(queryset=Cliente.objects.all())
    manicurista_id = serializers.PrimaryKeyRelatedField(queryset=Manicurista.objects.all())
    estado_id = serializers.PrimaryKeyRelatedField(queryset=EstadoCita.objects.all())
    cliente_nombre = serializers.SerializerMethodField()
    manicurista_nombre = serializers.SerializerMethodField()
    estado_nombre = serializers.SerializerMethodField()

    class Meta:
        model = CitaVenta
        fields = [
            'id',
            'cliente_id',
            'cliente_nombre',
            'manicurista_id',
            'manicurista_nombre',
            'estado_id',
            'estado_nombre',
            'Fecha',
            'Hora',
            'Descripcion',
            'Total',
        ]

    def get_cliente_nombre(self, obj):
        if obj.cliente_id:
            return f"{obj.cliente_id.nombre} {obj.cliente_id.apellido}"
        return "Cliente desconocido"

    def get_manicurista_nombre(self, obj):
        if obj.manicurista_id:
            return f"{obj.manicurista_id.nombre} {obj.manicurista_id.apellido}"
        return "Sin asignar"

    def get_estado_nombre(self, obj):
        if obj.estado_id:
            return obj.estado_id.Estado
        return "Estado desconocido"

    def validate(self, data):
        instance = self.instance  
        manicurista = data.get('manicurista_id', instance.manicurista_id if instance else None)
        cliente = data.get('cliente_id', instance.cliente_id if instance else None)
        fecha = data.get('Fecha', instance.Fecha if instance else None)
        hora = data.get('Hora', instance.Hora if instance else None)
        nuevo_estado = data.get('estado_id', instance.estado_id if instance else None)

        # Validación para cancelación de citas
        if instance and nuevo_estado:
            if nuevo_estado.Estado == "Cancelada" and instance.estado_id.Estado != "Cancelada":
                ahora = timezone.now()
                
                fecha_cita = fecha if fecha else instance.Fecha
                hora_cita = hora if hora else instance.Hora
                fecha_hora_cita = datetime.combine(fecha_cita, hora_cita)
                
                if timezone.is_naive(fecha_hora_cita):
                    fecha_hora_cita = timezone.make_aware(fecha_hora_cita)
                
                diferencia = fecha_hora_cita - ahora
                
                if diferencia < timedelta(hours=24):
                    horas_restantes = diferencia.total_seconds() / 3600
                    if horas_restantes <= 0:
                        raise serializers.ValidationError(
                            "No puedes cancelar una cita que ya pasó o está en curso."
                        )
                    else:
                        raise serializers.ValidationError(
                            f"No puedes cancelar una cita con menos de 24 horas de anticipación. "
                            f"Tu cita es en {horas_restantes:.1f} horas. "
                            f"Para cancelaciones de último momento, contacta directamente al establecimiento."
                        )

        if not (nuevo_estado and nuevo_estado.Estado == "Cancelada"):
            if not (manicurista and cliente and fecha and hora):
                return data  

            nueva_inicio = datetime.combine(fecha, hora)
            nueva_fin = nueva_inicio + timedelta(minutes=1)  

            cambios_en_agenda = (
                not instance or
                instance.manicurista_id != manicurista or
                instance.Fecha != fecha or
                instance.Hora != hora
            )

            if cambios_en_agenda:
                # Validación de novedades
                novedades = Novedades.objects.filter(manicurista_id=manicurista, Fecha=fecha)
                for novedad in novedades:
                    if novedad.HoraEntrada <= hora < novedad.HoraSalida:
                        raise serializers.ValidationError(
                            f"La manicurista tiene una novedad desde {novedad.HoraEntrada} hasta {novedad.HoraSalida} el {novedad.Fecha}."
                        )

                # Validación de citas de la manicurista
                citas_existentes = CitaVenta.objects.filter(
                    manicurista_id=manicurista,
                    Fecha=fecha,
                    estado_id__Estado__in=["Pendiente", "En proceso"]
                ).exclude(id=instance.id if instance else None)

                for cita in citas_existentes:
                    servicios_cita = ServicioCita.objects.filter(cita_id=cita.id)
                    if not servicios_cita.exists():
                        continue

                    duracion = sum((sc.servicio_id.duracion for sc in servicios_cita), timedelta())
                    cita_inicio = datetime.combine(cita.Fecha, cita.Hora)
                    cita_fin = cita_inicio + duracion

                    if nueva_inicio < cita_fin and nueva_fin > cita_inicio:
                        raise serializers.ValidationError(
                            f"La manicurista ya tiene una cita de {cita_inicio.time()} a {cita_fin.time()} ese día."
                        )

                # Validación de citas del cliente
                citas_cliente = CitaVenta.objects.filter(
                    cliente_id=cliente,
                    Fecha=fecha,
                    estado_id__Estado__in=["Pendiente", "En proceso"]
                ).exclude(id=instance.id if instance else None)

                for cita in citas_cliente:
                    servicios_cita = ServicioCita.objects.filter(cita_id=cita.id)
                    if not servicios_cita.exists():
                        continue

                    duracion = sum((sc.servicio_id.duracion for sc in servicios_cita), timedelta())
                    cita_inicio = datetime.combine(cita.Fecha, cita.Hora)
                    cita_fin = cita_inicio + duracion

                    if nueva_inicio < cita_fin and nueva_fin > cita_inicio:
                        raise serializers.ValidationError(
                            f"El cliente ya tiene una cita de {cita_inicio.time()} a {cita_fin.time()} ese día."
                        )

        return data
