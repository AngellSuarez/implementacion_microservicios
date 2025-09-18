from django.shortcuts import render
from rest_framework import  viewsets, status, permissions;
from rest_framework.response import Response;
from rest_framework.decorators import action;
from rest_framework.permissions import AllowAny;
from compra.models.compra_insumo import CompraInsumo
from abastecimiento.models.insumoAbastecimiento import InsumoAbastecimiento

from .models import Marca, Insumo
from .serializers import MarcaSerializer, InsumoSerializer

from utils.permisos import TienePermisoModulo
# Create your views here.

class MarcaViewSet(viewsets.ModelViewSet):
    queryset = Marca.objects.all()
    serializer_class = MarcaSerializer;
    permission_classes = [AllowAny]
    def destroy(self, request, *args, **kwargs):
        marca = self.get_object()
        if Insumo.objects.filter(marca_id=marca).exists():
            return Response(
                {"eliminado": False, "message": "No se puede eliminar la marca porque está asociada a uno o más insumos."},
                status=status.HTTP_400_BAD_REQUEST
            )
        self.perform_destroy(marca)
        return Response({"eliminado": True}, status=status.HTTP_200_OK)

class InsumoViewSet(viewsets.ModelViewSet):
    queryset = Insumo.objects.all()
    serializer_class = InsumoSerializer
    permission_classes = [TienePermisoModulo("Insumo")];
    def destroy(self, request, *args, **kwargs):
        insumo = self.get_object()

        # Verificar si el insumo está en alguna CompraInsumo con estado de compra no completada (1: Pendiente, 2: En proceso)
        compras_relacionadas = CompraInsumo.objects.filter(insumo_id=insumo)
        hay_compra_no_completada = compras_relacionadas.filter(
           compra_id__estadoCompra_id__id__in=[1, 2]
        ).exists()

        if hay_compra_no_completada:
          return Response(
            {
                "eliminado": False,
                "message": "No se puede eliminar el insumo porque está en una compra no completada o cancelada."
            },
            status=status.HTTP_400_BAD_REQUEST
        )

        # Verificar si el insumo está asociado a un abastecimiento sin reportar
        tiene_abastecimiento_sin_reportar = InsumoAbastecimiento.objects.filter(
          insumo_id=insumo,
          abastecimiento_id__estado="Sin reportar"
        ).exists()

        if tiene_abastecimiento_sin_reportar:
         return Response(
            {
                "eliminado": False,
                "message": "No se puede eliminar el insumo porque tiene un abastecimiento sin reportar."
            },
            status=status.HTTP_400_BAD_REQUEST
        )

        # Si pasa todas las validaciones, eliminar
        self.perform_destroy(insumo)
        return Response({"eliminado": True}, status=status.HTTP_200_OK)
