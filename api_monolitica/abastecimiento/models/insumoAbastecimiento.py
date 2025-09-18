from django.db import models

from usuario.models.manicurista_model import Manicurista
from insumo.models import Insumo
from django.utils import timezone

from .abastecimiento import Abastecimiento

class InsumoAbastecimiento(models.Model):
    ESTADOS_CHOICES = [
        ("Acabado","Acabado"),
        ("Uso medio","Uso medio"),
        ("Bajo","Bajo"),
        ("Sin usar","Sin usar"),
    ]
    
    insumo_id = models.ForeignKey(Insumo,on_delete=models.CASCADE)
    
    abastecimiento_id = models.ForeignKey(Abastecimiento,on_delete=models.CASCADE)
    cantidad = models.IntegerField(null=False,default=1)
    
    estado = models.CharField(max_length=30,null=False,default="Sin usar",choices = ESTADOS_CHOICES)
    
    comentario = models.TextField(null=True,blank=True) #leyly me quiero morir, no entiendo esta mierda
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
    
        # CORRECCIÓN: usar insumoabastecimiento_set (minúsculas + _set)
        relacionados = self.abastecimiento_id.insumoabastecimiento_set.all()
        pendientes = relacionados.filter(estado="Sin usar").exists()
    
        if not pendientes:
            self.abastecimiento_id.estado = "Reportado"
            self.abastecimiento_id.fecha_reporte = timezone.now().date()
            self.abastecimiento_id.save()