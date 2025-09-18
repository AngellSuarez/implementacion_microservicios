from django.db import models
from django.utils import timezone
from proveedor.models import Proveedor
from insumo.models import Insumo
from .estado_compra import EstadoCompra

class Compra(models.Model):
    fechaIngreso = models.DateField(null=False, default=timezone.now)
    fechaCompra = models.DateField(null=False, default=timezone.now)
 
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    IVA = models.DecimalField(max_digits=10, decimal_places=2, default=0.19)
    estadoCompra_id = models.ForeignKey(EstadoCompra, on_delete=models.CASCADE)
    proveedor_id = models.ForeignKey(Proveedor, on_delete=models.CASCADE)
    
    observacion = models.TextField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.fechaIngreso} - {self.fechaCompra} - {self.total} - {self.IVA} - {self.estadoCompra_id} - {self.proveedor_id}"