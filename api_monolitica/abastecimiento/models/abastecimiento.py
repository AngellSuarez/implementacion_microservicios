from django.db import models

from usuario.models.manicurista_model import Manicurista

from django.utils import timezone

class Abastecimiento(models.Model):
    
    ESTADOS_CHOICES = [
        ("Sin reportar","Sin Reportar"),
        ("Reportado","Reportado"),
        
    ]
    
    fecha_creacion = models.DateField(null=False,auto_now_add=True)
    
    manicurista_id = models.ForeignKey(Manicurista,on_delete=models.CASCADE)
    estado = models.CharField(max_length=30,choices=ESTADOS_CHOICES,default="Sin reportar")
    fecha_reporte = models.DateField(null=True,blank=True)
    
    def __str__(self):
        return f"{self.fecha_creacion} - {self.manicurista_id}";