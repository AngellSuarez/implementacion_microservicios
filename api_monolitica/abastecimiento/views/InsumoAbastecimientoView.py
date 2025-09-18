# views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction
from django.shortcuts import get_object_or_404
from ..models.abastecimiento import Abastecimiento
from ..models.insumoAbastecimiento import InsumoAbastecimiento
from ..serializer.insumoAbastecimientoSerializer import InsumoAbastecimientoSerializer

class InsumoAbastecimientoViewSet(viewsets.ModelViewSet):
    queryset = InsumoAbastecimiento.objects.all()
    serializer_class = InsumoAbastecimientoSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtrar por abastecimiento si se proporciona
        abastecimiento_id = self.request.query_params.get('abastecimiento', None)
        if abastecimiento_id:
            queryset = queryset.filter(abastecimiento_id=abastecimiento_id)
        
        # Filtrar por insumo si se proporciona
        insumo_id = self.request.query_params.get('insumo', None)
        if insumo_id:
            queryset = queryset.filter(insumo_id=insumo_id)
            
        # Filtrar por estado si se proporciona
        estado = self.request.query_params.get('estado', None)
        if estado:
            queryset = queryset.filter(estado=estado)
        
        return queryset.order_by('-id')
    
    @transaction.atomic
    def destroy(self, request, *args, **kwargs):
        """Al eliminar un InsumoAbastecimiento, devolver el stock al insumo"""
        instance = self.get_object()
        
        # Devolver la cantidad al stock del insumo
        insumo = instance.insumo_id
        insumo.stock += instance.cantidad
        insumo.save()
        
        return super().destroy(request, *args, **kwargs)
    
    @action(detail=True, methods=['patch'])
    def cambiar_estado(self, request, pk=None):
        """Cambiar solo el estado del insumo abastecimiento"""
        instance = self.get_object()
        nuevo_estado = request.data.get('estado')
        
        if nuevo_estado not in dict(InsumoAbastecimiento.ESTADOS_CHOICES):
            return Response(
                {'error': 'Estado no válido'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        instance.estado = nuevo_estado
        instance.save()
        
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def por_estado(self, request):
        """Obtener insumos abastecimiento agrupados por estado"""
        estados = {}
        for estado_key, estado_label in InsumoAbastecimiento.ESTADOS_CHOICES:
            insumos = self.get_queryset().filter(estado=estado_key)
            estados[estado_key] = {
                'label': estado_label,
                'count': insumos.count(),
                'insumos': InsumoAbastecimientoSerializer(insumos, many=True).data
            }
        
        return Response(estados)
    
    @action(detail=False, methods=['get'])
    def sin_usar(self, request):
        """Obtener todos los insumos sin usar"""
        insumos = self.get_queryset().filter(estado='Sin usar')
        serializer = self.get_serializer(insumos, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def realizar_reporte(self, request):
        """Realizar reporte masivo de insumos"""
        abastecimiento_id = request.data.get('abastecimiento_id')
        insumos_reporte = request.data.get('insumos_reporte', [])
        
        if not abastecimiento_id:
            return Response(
                {'error': 'ID de abastecimiento requerido'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not insumos_reporte:
            return Response(
                {'error': 'Lista de insumos para reporte requerida'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            abastecimiento = Abastecimiento.objects.get(id=abastecimiento_id)
        except Abastecimiento.DoesNotExist:
            return Response(
                {'error': 'Abastecimiento no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        insumos_actualizados = []
        errores = []
        
        with transaction.atomic():
            for insumo_data in insumos_reporte:
                try:
                    insumo_id = insumo_data.get('id')
                    if not insumo_id:
                        errores.append("ID de insumo requerido")
                        continue
                    
                    insumo_abastecimiento = InsumoAbastecimiento.objects.get(
                        id=insumo_id,
                        abastecimiento_id=abastecimiento
                    )
                    
                    if 'estado' in insumo_data:
                        insumo_abastecimiento.estado = insumo_data['estado']
                    if 'comentario' in insumo_data:
                        insumo_abastecimiento.comentario = insumo_data['comentario']
                    
                    insumo_abastecimiento.save()
                    insumos_actualizados.append({
                        'id': insumo_abastecimiento.id,
                        'insumo': insumo_abastecimiento.insumo_id.nombre,
                        'estado': insumo_abastecimiento.estado,
                        'comentario': insumo_abastecimiento.comentario
                    })
                    
                except InsumoAbastecimiento.DoesNotExist:
                    errores.append(f"InsumoAbastecimiento con ID {insumo_id} no encontrado")
                except Exception as e:
                    errores.append(f"Error procesando insumo {insumo_id}: {str(e)}")
        
        abastecimiento.refresh_from_db()
        
        return Response({
            'mensaje': f'Reporte procesado. {len(insumos_actualizados)} insumos actualizados',
            'abastecimiento_estado': abastecimiento.estado,
            'fecha_reporte': abastecimiento.fecha_reporte,
            'insumos_actualizados': insumos_actualizados,
            'errores': errores if errores else None
        })