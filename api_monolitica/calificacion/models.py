from django.db import models

class Calificacion(models.Model):
    OPCIONES = [
        (1, 'Muy Bien'),
        (2, 'Bien'),
        (3, 'Mal'),
        (4, 'Muy Mal'),
    ]

    puntuacion = models.IntegerField(choices=OPCIONES)
    comentario = models.TextField(blank=True)
    imagen = models.ImageField(upload_to='calificaciones/', blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Calificación {self.get_puntuacion_display()} - {self.fecha_creacion.date()}"
