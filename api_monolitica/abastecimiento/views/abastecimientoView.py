# views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction
from django.shortcuts import get_object_or_404
from ..models.abastecimiento import Abastecimiento
from ..models.insumoAbastecimiento import InsumoAbastecimiento
from ..serializer.abastecimientoSerializer import AbastecimientoSerializer
from ..serializer.abastecimientoConInsumos import AbastecimientoConInsumosSerializer
from ..serializer.insumoAbastecimientoSerializer import InsumoAbastecimientoSerializer
from usuario.models.manicurista_model import Manicurista
from django.db.models import Count

from utils.permisos import TienePermisoModulo

class AbastecimientoViewSet(viewsets.ModelViewSet):
    queryset = Abastecimiento.objects.all().order_by('-fecha_creacion')
    serializer_class = AbastecimientoSerializer
    permission_classes = [TienePermisoModulo("Abastecimiento")];
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return AbastecimientoConInsumosSerializer
        return AbastecimientoSerializer
    
    @action(detail=True, methods=['get'])
    def insumos(self, request, pk=None):
        """Obtener todos los insumos de un abastecimiento específico"""
        abastecimiento = self.get_object()
        insumos = InsumoAbastecimiento.objects.filter(abastecimiento_id=abastecimiento)
        serializer = InsumoAbastecimientoSerializer(insumos, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def marcar_reportado(self, request, pk=None):
        """Marcar manualmente un abastecimiento como reportado"""
        abastecimiento = self.get_object()
        
        if abastecimiento.estado == 'Reportado':
            return Response(
                {'error': 'El abastecimiento ya está reportado'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Marcar todos los insumos como usados y el abastecimiento como reportado
        with transaction.atomic():
            InsumoAbastecimiento.objects.filter(
                abastecimiento_id=abastecimiento,
                estado='Sin usar'
            ).update(estado='Uso medio')
            
            abastecimiento.estado = 'Reportado'
            abastecimiento.save()
        
        serializer = self.get_serializer(abastecimiento)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def sin_reportar(self, request):
        """Obtener todos los abastecimientos sin reportar"""
        abastecimientos = self.queryset.filter(estado='Sin reportar')
        serializer = self.get_serializer(abastecimientos, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def reportados(self, request):
        """Obtener todos los abastecimientos reportados"""
        abastecimientos = self.queryset.filter(estado='Reportado')
        serializer = self.get_serializer(abastecimientos, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def agregar_insumos(self, request, pk=None):
        """Agregar múltiples insumos a un abastecimiento"""
        abastecimiento = self.get_object()
        insumos_data = request.data.get('insumos', [])

        if not insumos_data:
            return Response(
                {'error': 'Se requiere una lista de insumos'},
                status=status.HTTP_400_BAD_REQUEST
            )

        insumos_creados = []
        errores = []

        with transaction.atomic():
            for i, insumo_data in enumerate(insumos_data):
                try:
                    insumo_id = insumo_data.get('insumo_id')
                    if not insumo_id:
                        errores.append(f"Insumo {i+1}: ID de insumo requerido")
                        continue
                    
                    data = {
                        'insumo_id': insumo_id,
                        'abastecimiento_id': abastecimiento.id,
                        'cantidad': insumo_data.get('cantidad', 1),
                        'comentario': insumo_data.get('comentario', '')
                    }

                    serializer = InsumoAbastecimientoSerializer(data=data)
                    if serializer.is_valid():
                        insumo_creado = serializer.save()
                        insumos_creados.append(serializer.data)
                    else:
                        errores.append(f"Insumo {i+1}: {serializer.errors}")

                except Exception as e:
                    errores.append(f"Insumo {i+1}: {str(e)}")

        if errores:
            return Response(
                {
                    'errores': errores,
                    'insumos_creados': insumos_creados,
                    'parcialmente_exitoso': len(insumos_creados) > 0
                },
                status=status.HTTP_207_MULTI_STATUS if insumos_creados else status.HTTP_400_BAD_REQUEST
            )

        return Response({
            'mensaje': f'Se agregaron {len(insumos_creados)} insumos exitosamente',
            'insumos_creados': insumos_creados
        })
        
    @transaction.atomic
    def perform_destroy(self, instance):
        for insumo_abast in instance.insumoabastecimiento_set.all():
            if insumo_abast.estado == 'Sin usar':
                insumo = insumo_abast.insumo_id
                insumo.stock += insumo_abast.cantidad
                insumo.save()
            insumo_abast.delete()

        instance.delete()
        
    @action(detail=False, methods=['get'])
    def recientes(self, request):
        """Obtener los 3 abastecimientos más recientes con sus insumos"""
        abastecimientos = Abastecimiento.objects.all().order_by('-fecha_creacion')[:3]
        serializer = AbastecimientoConInsumosSerializer(abastecimientos, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def top_manicuristas(self, request):
        """Obtener top 3 manicuristas por cantidad de abastecimientos"""
        top = (
            Abastecimiento.objects
            .values('manicurista_id__nombre', 'manicurista_id__apellido')
            .annotate(pedidos=Count('id'))
            .order_by('-pedidos')[:3]
        )

        results = [
          {
            'nombre': f"{item['manicurista_id__nombre']} {item['manicurista_id__apellido']}",
            'pedidos': item['pedidos']
          }
          for item in top
        ]

        return Response(results)
    
    
    @action(detail=False, methods=['get'])
    def consumos_reportados(self, request):
       """Devuelve los insumos reportados para un manicurista específico"""
       manicurista_id = request.query_params.get('manicurista_id')
       if not manicurista_id:
          return Response({'error': 'Falta el parámetro manicurista_id'}, status=400)

       try:
          insumos = InsumoAbastecimiento.objects.exclude(estado='Sin usar') \
            .filter(abastecimiento_id__manicurista_id=manicurista_id) \
            .select_related('insumo_id', 'abastecimiento_id') \
            .order_by('-abastecimiento_id__fecha_creacion')[:3]

          data = []
          for insumo in insumos:
            insumo_nombre = getattr(insumo.insumo_id, 'nombre', 'Desconocido')
            fecha = getattr(insumo.abastecimiento_id, 'fecha_creacion', None)

            data.append({
                'insumo': str(insumo_nombre),
                'cantidad': insumo.cantidad,
                'estadoInsumo': insumo.estado,
                'fecha': fecha
            })

          return Response(data)

       except Exception as e:
          return Response({'error': f'Error al procesar los consumos: {str(e)}'}, status=500)


