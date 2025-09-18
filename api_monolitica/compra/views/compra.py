from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from ..serializers.compra import ComprasSerializer
from ..serializers.compra_insumo import CompraInsumoSerializer  # Importa el serializer de CompraInsumo
from ..models.compra import Compra
from ..models.estado_compra import EstadoCompra
from ..models.compra_insumo import CompraInsumo  # Importa el modelo de CompraInsumo
from proveedor.models import Proveedor
from insumo.models import Insumo  # Importa el modelo de Insumo

from utils.permisos import TienePermisoModulo


class CompraViewSet(viewsets.ModelViewSet):
    queryset = Compra.objects.all()
    serializer_class = ComprasSerializer
    http_method_names = ['get', 'post', 'delete', 'head']
    permission_classes = [TienePermisoModulo("Compra")];

    def get_queryset(self):
        queryset = Compra.objects.all()

        proveedor_id = self.request.query_params.get('proveedor_id', None)
        if proveedor_id is not None:
            queryset = queryset.filter(proveedor_id=proveedor_id)

        estado_id = self.request.query_params.get('estadoCompra_id', None)
        if estado_id is not None:
            queryset = queryset.filter(estadoCompra_id=estado_id)

        fecha_inicio = self.request.query_params.get('fecha_inicio', None)
        fecha_fin = self.request.query_params.get('fecha_fin', None)

        if fecha_inicio is not None and fecha_fin is not None:
            queryset = queryset.filter(fechaCompra__range=[fecha_inicio, fecha_fin])

        return queryset

    def create(self, request, *args, **kwargs):
        data = request.data.copy()

        # Asignar estado por defecto si no viene en la petición
        if 'estadoCompra_id' not in data or not data['estadoCompra_id']:
            data['estadoCompra_id'] = 2  # Asume que 1 es el ID del estado "Pendiente"

        serializer = self.get_serializer(data=data)
        if serializer.is_valid():
           serializer.save()
           return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()

        if instance.estadoCompra_id.id == 4:  # Asumiendo que 4 es "Cancelada"
            instance.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            estado_cancelada = EstadoCompra.objects.get(id=4)
            instance.estadoCompra_id = estado_cancelada
            instance.save()
            serializer = self.get_serializer(instance)
            return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def cambiar_estado(self, request, pk=None):
        compra = self.get_object()
        estado_id = request.data.get('estadoCompra_id', None)
        observacion = request.data.get('observacion', None)

        if estado_id is None:
          return Response(
            {"error": "Se requiere el parámetro estado_id"},
            status=status.HTTP_400_BAD_REQUEST
        )

        try:
            nuevo_estado = EstadoCompra.objects.get(id=estado_id)
            compra.estadoCompra_id = nuevo_estado

            # Solo guardar observación si se está cancelando (ID 4)
            if nuevo_estado.id == 4 and observacion:
               compra.observacion = observacion

            compra.save()

            # Actualizar stock si se completa (ID 3)
            if nuevo_estado.id == 3:
               self._actualizar_stock_al_completar_compra(compra)

            serializer = self.get_serializer(compra)
            return Response(serializer.data)

        except EstadoCompra.DoesNotExist:
          return Response(
            {"error": f"El estado con ID {estado_id} no existe"},
            status=status.HTTP_400_BAD_REQUEST
        )


    def _actualizar_stock_al_completar_compra(self, compra):
        compra_insumos = CompraInsumo.objects.filter(compra_id=compra)
        for compra_insumo in compra_insumos:
            insumo = compra_insumo.insumo_id
            cantidad_comprada = compra_insumo.cantidad
            insumo.stock += cantidad_comprada
            insumo.save()

    @action(detail=False, methods=['get'])
    def by_proveedor(self, request):
        proveedor_id = request.query_params.get('proveedor_id', None)
        if proveedor_id is None:
            return Response({"error": "proveedor_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        compras = Compra.objects.filter(proveedor_id=proveedor_id)
        serializer = self.get_serializer(compras, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def by_estado(self, request):
        estado_id = request.query_params.get('estadoCompra_id', None)
        if estado_id is None:
            return Response({"error": "estado_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        compras = Compra.objects.filter(estadoCompra_id=estado_id)
        serializer = self.get_serializer(compras, many=True)
        return Response(serializer.data)