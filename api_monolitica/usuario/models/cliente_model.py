from django.db import models
from ..models.usuario_model import Usuario;

class Manicurista(models.Model):
    ESTADOS_CHOICES = (
        ("Activo", "Activo"),
        ("Inactivo", "Inactivo"),
    )

    TIPO_DOCUMENTO_CHOICES = (
        ("CC", "cedula de ciudadania"),
        ("CE", "cedula de extranjeria"),
        ("TI", "tarjeta de identidad"),
        ("RC", "registro civil"),
        ("PA", "pasaporte"),
    )

    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, primary_key=True)
    
    nombre = models.CharField(max_length=30, null=False)
    
    apellido = models.CharField(max_length=30, null=False)
    
    tipo_documento = models.CharField(max_length=2, choices=TIPO_DOCUMENTO_CHOICES, null=False)
    
    numero_documento = models.CharField(max_length=15, unique=True, null=False)
    
    correo = models.EmailField(max_length=60, unique=True, null=False)
    
    celular = models.CharField(max_length=13, unique=True, null=False)
    
    estado = models.CharField(max_length=8, choices=ESTADOS_CHOICES, default="Activo")
    
    fecha_nacimiento = models.DateField(null=False)
    
    fecha_contratacion = models.DateField(null=False)

    def __str__(self):
        return f"{self.nombre} - {self.apellido} - {self.correo} - ({self.estado})"