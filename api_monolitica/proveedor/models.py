from django.db import models

# Create your models here.
class Proveedor(models.Model):
    TIPO_PERSONA_CHOICES = (
        ("NATURAL", "Natural"),
        ("JURIDICA", "Jurídica"),
    )

    TIPO_DOCUMENTO_CHOICES = (
        ("NIT", "NIT"),
        ("CC", "Cédula de Ciudadanía"),
        ("CE", "Cédula de Extranjería"),
    )

    ESTADO_CHOICES = (
        ("Activo", "Activo"),
        ("Inactivo", "Inactivo"),
    )

    tipo_persona = models.CharField(max_length=10, choices=TIPO_PERSONA_CHOICES)
    tipo_documento = models.CharField(max_length=3, choices=TIPO_DOCUMENTO_CHOICES)
    numero_documento = models.CharField(max_length=15, unique=True)
    
    nombre_empresa = models.CharField(max_length=60, null=True, blank=True)

    # Datos generales de contacto
    telefono = models.CharField(max_length=15)
    email = models.EmailField(max_length=60, unique=True)
    direccion = models.CharField(max_length=60)
    ciudad = models.CharField(max_length=60)

    # Representante (solo para NIT / empresa)
    nombre_representante = models.CharField(max_length=60, null=True, blank=True)
    apellido_representante = models.CharField(max_length=60, null=True, blank=True)
    telefono_representante = models.CharField(max_length=15, null=True, blank=True)
    email_representante = models.EmailField(max_length=60, null=True, blank=True)

    # Estado del proveedor
    estado = models.CharField(
        max_length=10,
        choices=ESTADO_CHOICES,
        default="Activo"
    )

    def __str__(self):
        return f"{self.nombre_empresa or self.nombre_representante} - {self.tipo_persona} - {self.numero_documento}"
