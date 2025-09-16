from django.contrib import admin
from .models import Rol, Permiso, Permiso_Rol
# Register your models here.
admin.site(Rol)
admin.site(Permiso)
admin.site(Permiso_Rol)