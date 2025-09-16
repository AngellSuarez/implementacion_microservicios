from django.db import models

from ..models.estado_cita_model import EstadoCita
from usuario.models.manicurista_model import Manicurista
from usuario.models.cliente_model import Cliente

class CitaVenta(models.Model):
    estado_id = models.ForeignKey(EstadoCita,on_delete=models.CASCADE,null=False)
    
    manicurista_id = models.ForeignKey(
        Manicurista,
        on_delete=models.SET_NULL,  
        null=True,               
        blank=True
    )
    
    cliente_id = models.ForeignKey(Cliente,on_delete=models.SET_NULL ,null=True, blank=True)
    
    Fecha = models.DateField(null=False)
    
    Hora = models.TimeField(null=False)
    
    Descripcion = models.TextField()
    
    Total = models.DecimalField(max_digits=10,decimal_places=2,null=False,default=0.00)
    
    def __str__(self):
        return f"{self.estado_id} - {self.manicurista_id} - {self.cliente_id} - {self.Fecha}- {self.Hora} - {self.Descripcion} - {self.Total}";

