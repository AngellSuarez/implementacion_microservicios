from django.contrib import admin
from .models.cliente_model import Cliente
from .models.usuario_model import Usuario
from .models.manicurista_model import Manicurista
# Register your models here.
admin.site(Usuario)
admin.site(Manicurista)
admin.site(Cliente)