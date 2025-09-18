import requests
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.utils.timezone import now
from django.db.models import Count, Q
from datetime import timedelta
from django.db import models
from django.conf import settings # Usar settings para URL de microservicios

from ..models.cita_venta_model import CitaVenta
from ..models.estado_cita_model import EstadoCita
from ..models.servicio_cita_model import ServicioCita

from ..serializers.servicio_cita_serializer import ServicioCitaSerializer

from utils.email_utils import enviar_correo_confirmacion

class ServicioCitaViewSet(viewsets.ModelViewSet):
    queryset = ServicioCita.objects.all()
    serializer_class = ServicioCitaSerializer
    
    def get_queryset(self):
        cita_id = self.request.query_params.get('cita_id')
        if cita_id:
            return ServicioCita.objects.filter(cita_id=cita_id)
        return ServicioCita.objects.all()
    
    def _obtener_precio_servicio(self, servicio_id):
        """Función auxiliar para obtener el precio de un servicio desde su API."""
        try:
            # URL del microservicio de servicios
            url = f"http://127.0.0.1:8001/micro-servicios/servicio/{servicio_id}/"
            response = requests.get(url)
            print(response)
            print(url)
            response.raise_for_status() # Lanza un error para códigos de estado
            return response.json().get('precio')
        except requests.exceptions.RequestException:
            return None

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'], url_path='batch')
    def create_batch(self, request):
        data = request.data
        if not isinstance(data, list):
            return Response({"error": "Se esperaba una lista de objetos"}, status=status.HTTP_400_BAD_REQUEST)

        # Aquí es donde se debe optimizar la lógica
        servicios_a_crear = []
        errors = []
        citas_servicios = {}
        
        for entry in data:
            if 'servicio_id' in entry and 'subtotal' not in entry:
                precio = self._obtener_precio_servicio(entry['servicio_id'])
                if precio is None:
                    errors.append({"error": f"El servicio con ID {entry['servicio_id']} no existe o no se pudo obtener su precio."})
                    continue
                entry['subtotal'] = precio
            
            servicios_a_crear.append(entry)
        
        serializer = self.get_serializer(data=servicios_a_crear, many=True)
        
        if serializer.is_valid():
            instances = serializer.save()
            
            # Procesar los servicios creados para el correo
            for item in instances:
                cita = item.cita_id
                cliente = cita.cliente_id
                
                if cita.id not in citas_servicios:
                    citas_servicios[cita.id] = {
                        "cita": cita,
                        "cliente": cliente,
                        "servicios": []
                    }
            
                # petición HTTP al microservicio de servicios o lo pases desde el frontend
                servicios_a_crear_dict = {s['servicio_id']: s for s in servicios_a_crear}   
                servicio_data = servicios_a_crear_dict.get(item.servicio_id)
                
                citas_servicios[cita.id]["servicios"].append({
                    "nombre":item.nombre,
                    "subtotal": item.subtotal
                })
            
            # Enviar correos
            for data in citas_servicios.values():
                enviar_correo_confirmacion(
                    destinatario=data["cliente"].correo,
                    nombre_cliente=data["cliente"].nombre,
                    fecha=data["cita"].Fecha,
                    hora=data["cita"].Hora,
                    servicios=data["servicios"]
                )

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            errors.extend(serializer.errors)
            return Response({"created": [], "errors": errors}, status=status.HTTP_400_BAD_REQUEST)
    
    # ... (código de las acciones de estadísticas y destroy) ...
    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            cita = instance.cita_id
            
            self.perform_destroy(instance)
            
            # Recalcular el total de la cita después de eliminar el servicio
            nuevo_total = ServicioCita.objects.filter(cita_id=cita).aggregate(
                total=Sum('subtotal')
            )['total'] or 0
            
            cita.Total = nuevo_total
            cita.save()
            
            print(f"✅ Total actualizado para la cita {cita.id}: ${nuevo_total}")
            
            return Response(status=status.HTTP_204_NO_CONTENT)
            
        except ServicioCita.DoesNotExist:
            return Response(
                {"error": "El servicio de la cita no existe."},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": f"Ocurrió un error al eliminar el servicio de la cita: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            
    @action(detail=False, methods=['get'], url_path='servicios-mas-vendidos-mes')
    def servicios_mas_vendidos_mes(self, request):
        try:
            hoy = now().date()
            inicio_mes = hoy.replace(day=1)

            # Usar Q object para manejar la consulta de estado de forma segura
            query = Q(cita_id__Fecha__gte=inicio_mes) & Q(cita_id__Fecha__lte=hoy)
            query &= Q(cita_id__estado_id__Estado='Terminada') 
            
            servicios_vendidos = (
                ServicioCita.objects.filter(query)
                .values('servicio_id', 'servicio_id__nombre')
                .annotate(ventas=Count('id'))
                .order_by('-ventas')[:3]
            )

            data = [
                {"name": item['servicio_id__nombre'], "ventas": item['ventas']}
                for item in servicios_vendidos
            ]

            return Response(data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": f"Error al obtener los servicios más vendidos: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'], url_path='servicios-semana-manicurista')
    def servicios_semana_manicurista(self, request):
        try:
            manicurista_id = request.query_params.get('manicurista_id')
            if not manicurista_id:
                return Response(
                    {"error": "Se requiere el parámetro 'manicurista_id'."}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

            hoy = now().date()
            inicio_semana = hoy - timedelta(days=hoy.weekday())
            fin_semana = inicio_semana + timedelta(days=6)

            query = Q(cita_id__Fecha__range=(inicio_semana, fin_semana))
            query &= Q(cita_id__manicurista_id=manicurista_id)
            query &= Q(cita_id__estado_id__Estado='Terminada')

            servicios_semana = (
                ServicioCita.objects.filter(query)
                .values('servicio_id', 'servicio_id__nombre')
                .annotate(cantidad=Count('id'))
                .order_by('-cantidad')[:5]
            )

            data = [
                {"servicio": item['servicio_id__nombre'], "cantidad": item['cantidad']}
                for item in servicios_semana
            ]

            return Response(data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": f"Error al obtener los servicios de la semana: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )