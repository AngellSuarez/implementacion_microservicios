from django.contrib import admin
from .models import Rol, Permiso, Permiso_Rol
# Register your models here.
admin.site.register(Rol)
admin.site.register(Permiso)
admin.site.register(Permiso_Rol)