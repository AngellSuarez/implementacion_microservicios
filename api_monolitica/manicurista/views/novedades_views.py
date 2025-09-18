from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db.models import Q
from datetime import time

from ..models.novedades_model import Novedades
from ..serializers.novedad_serializer import NovedadesSerializer

from utils.permisos import TienePermisoModulo

class NovedadesViewSet(viewsets.ModelViewSet):
    serializer_class = NovedadesSerializer
    queryset = Novedades.objects.all()
    permission_classes = [TienePermisoModulo("Novedades")];

    def get_queryset(self):
        queryset = Novedades.objects.all()
        manicurista_id = self.request.query_params.get('manicurista_id')

        if manicurista_id:
           queryset = queryset.filter(manicurista_id=manicurista_id)

        return queryset
    
    @action(detail=False, methods=['get'], url_path='horarios-disponibles')
    def horarios_disponibles(self, request):
        """
        Endpoint para obtener los horarios disponibles para una manicurista en una fecha específica
        """
        manicurista_id = request.query_params.get('manicurista_id')
        fecha = request.query_params.get('fecha')
        
        if not manicurista_id or not fecha:
            return Response(
                {'error': 'Se requieren los parámetros manicurista_id y fecha'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Obtener novedades existentes para la manicurista en la fecha especificada
        novedades_existentes = Novedades.objects.filter(
            manicurista_id=manicurista_id,
            Fecha=fecha
        ).order_by('HoraEntrada')
        
        # Crear lista de horarios ocupados
        horarios_ocupados = []
        for novedad in novedades_existentes:
            horarios_ocupados.append({
                'inicio': novedad.HoraEntrada.strftime('%H:%M'),
                'fin': novedad.HoraSalida.strftime('%H:%M'),
                'motivo': novedad.Motivo
            })
        
        # Calcular horarios disponibles
        horarios_disponibles = []
        hora_inicio_dia = time(8, 0)
        hora_fin_dia = time(18, 0)
        
        if not novedades_existentes:
            # Si no hay novedades, todo el día está disponible
            horarios_disponibles.append({
                'inicio': hora_inicio_dia.strftime('%H:%M'),
                'fin': hora_fin_dia.strftime('%H:%M')
            })
        else:
            # Verificar si hay tiempo disponible antes de la primera novedad
            primera_novedad = novedades_existentes.first()
            if primera_novedad.HoraEntrada > hora_inicio_dia:
                horarios_disponibles.append({
                    'inicio': hora_inicio_dia.strftime('%H:%M'),
                    'fin': primera_novedad.HoraEntrada.strftime('%H:%M')
                })
            
            # Verificar espacios entre novedades
            for i in range(len(novedades_existentes) - 1):
                novedad_actual = novedades_existentes[i]
                novedad_siguiente = novedades_existentes[i + 1]
                
                if novedad_actual.HoraSalida < novedad_siguiente.HoraEntrada:
                    horarios_disponibles.append({
                        'inicio': novedad_actual.HoraSalida.strftime('%H:%M'),
                        'fin': novedad_siguiente.HoraEntrada.strftime('%H:%M')
                    })
            
            # Verificar si hay tiempo disponible después de la última novedad
            ultima_novedad = novedades_existentes.last()
            if ultima_novedad.HoraSalida < hora_fin_dia:
                horarios_disponibles.append({
                    'inicio': ultima_novedad.HoraSalida.strftime('%H:%M'),
                    'fin': hora_fin_dia.strftime('%H:%M')
                })
        
        return Response({
            'horarios_ocupados': horarios_ocupados,
            'horarios_disponibles': horarios_disponibles
        })

    def create(self, request, *args, **kwargs):
        """
        Override del método create para proporcionar mensajes de error más detallados
        """
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        except Exception as e:
            return Response(
                {'errores': {'general': [str(e)]}}, 
                status=status.HTTP_400_BAD_REQUEST
            )

    def update(self, request, *args, **kwargs):
        """
        Override del método update para proporcionar mensajes de error más detallados
        """
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        try:
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {'errores': {'general': [str(e)]}}, 
                status=status.HTTP_400_BAD_REQUEST
            )