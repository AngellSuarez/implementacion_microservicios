from django.db import models
from usuario.models.manicurista_model import Manicurista

class Liquidacion(models.Model):
    manicurista_id = models.ForeignKey(Manicurista,on_delete=models.CASCADE,null=False)
    FechaInicial = models.DateField(null=False);
    TotalGenerado = models.DecimalField(max_digits=10,decimal_places=2,null=False,default=0.00)
    Comision = models.DecimalField(max_digits=10,decimal_places=2,null=False,default=0.00)
    Local = models.DecimalField(max_digits=10,decimal_places=2,null=False,default=0.00)
    FechaFinal = models.DateField(null=False)