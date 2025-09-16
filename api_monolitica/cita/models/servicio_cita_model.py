from django.db import models

# from servicio.models import Servicio
from .cita_venta_model import CitaVenta

class ServicioCita(models.Model):
    cita_id = models.ForeignKey(CitaVenta,on_delete=models.CASCADE,null=False)
    # servicio_id = models.ForeignKey(Servicio,on_delete=models.CASCADE,null=False)
    servicio_id = models.IntegerField(null=False,blank=False)
    subtotal = models.DecimalField(max_digits=10,decimal_places=2,null=False,default=0.00)
    
    def __str__(self):
        return f"{self.cita_id} - {self.servicio_id} - {self.subtotal}";
