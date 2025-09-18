from django.shortcuts import render
from rest_framework import  viewsets, status, permissions;
from rest_framework.response import Response;
from rest_framework.decorators import action;
from rest_framework.permissions import AllowAny;

from .models import Proveedor
from compra.models.compra import Compra
from .serializers import ProveedorSerializer

from utils.permisos import TienePermisoModulo

# Create your views here.

class ProveedorViewSet(viewsets.ModelViewSet):
    queryset = Proveedor.objects.all()
    serializer_class = ProveedorSerializer;
    permission_classes = [TienePermisoModulo("Proveedor")];
    
    def destroy(self,request,*args,**kwargs):
        instance = self.get_object();
        
        compras_pendientes = Compra.objects.filter(estadoCompra_id=2).exists()
        compras_proceso = Compra.objects.filter(estadoCompra_id=1).exists()
        compras_devuelta = Compra.objects.filter(estadoCompra_id=5).exists()
        
        if compras_proceso or compras_pendientes or compras_devuelta:
            instance.estado = "Inactivo"
            instance.save()
            return Response(
                {"message":"El proveedor tiene compras: pendientes, en proceso o devueltas, por lo cual solo se desativo"}, status = status.HTTP_200_OK
            )
        else:
            instance.delete()
            return Response({
                "message":"El proveedor no cuenta con compras pendientes, en proceso o devueltas por lo cual se elimino"
            }, status = status.HTTP_204_NO_CONTENT)