from django.contrib import admin
from .models.cita_venta_model import CitaVenta
from .models.estado_cita_model import EstadoCita
from .models.servicio_cita_model import ServicioCita
# Register your models here.

admin.site.register(EstadoCita)
admin.site.register(CitaVenta)
admin.site.register(ServicioCita)
