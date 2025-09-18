from django.db import models;
from insumo.models import Insumo;

from .compra import Compra;

    
class CompraInsumo(models.Model):
    
    cantidad = models.IntegerField(null=False,default=1)
    
    precioUnitario = models.DecimalField(max_digits=10,decimal_places=2,null=False,default=1)
    
    subtotal = models.DecimalField(max_digits=10,decimal_places=2,null=False,default=0)
    
    compra_id = models.ForeignKey(Compra,on_delete=models.CASCADE)
    
    insumo_id = models.ForeignKey(Insumo,on_delete=models.CASCADE)
    
    def __str__(self):
        return f"{self.cantidad} - {self.precioUnitario} - {self.subtotal} - {self.compra_id} - {self.insumo_id}";