from django.contrib import admin
from .models.liquidacion_model import Liquidacion
from .models.novedades_model import Novedades

# Register your models here.
admin.site.register(Liquidacion)
admin.site.register(Novedades)