from django.db import models;
from django.utils import timezone;

class EstadoCompra(models.Model):
    Estado = models.CharField(max_length=40,null=False);
    
    def __str__(self):
        return self.Estado;