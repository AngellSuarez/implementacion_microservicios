from django.db import models

# Create your models here.
from django.db import models
from django.utils import timezone
from datetime import timedelta

class Servicio(models.Model):
    ESTADOS_CHOICES = (
        ("Activo", "Activo"),
        ("Inactivo", "Inactivo"),
    )

    TIPO_CHOICES = (
        ("Manicure", "Manicure"),
        ("Pedicure", "Pedicure"),
        ("Retiros", "Retiros"),
    )

    nombre = models.CharField(max_length=40, null=False)
    descripcion = models.TextField()
    
    precio = models.DecimalField(max_digits=10, decimal_places=2, null=False, default=0.00)
    
    duracion = models.DurationField(default=timedelta(minutes=30)) 
    
    estado = models.CharField(max_length=40, null=False, choices=ESTADOS_CHOICES, default="Activo")
    
    tipo = models.CharField(max_length=40, null=False, choices=TIPO_CHOICES, default="Manicure")  
    
    url_imagen = models.URLField(max_length=500, null=True, blank=True)  
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.nombre} - {self.precio} - {self.tipo}"
