from django.db import models
from usuario.models.manicurista_model import Manicurista

class Novedades(models.Model):
    manicurista_id = models.ForeignKey(Manicurista,on_delete=models.CASCADE,null=False);
    Fecha = models.DateField(null=False)
    HoraEntrada = models.TimeField(null=False)
    HoraSalida = models.TimeField(null=False)
    Motivo = models.TextField()
    
    def __str__(self):
        return f" {self.Fecha} - {self.HoraEntrada} - {self.HoraSalida} - {self.Motivo}";