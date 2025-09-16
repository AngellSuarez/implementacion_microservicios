from rest_framework import serializers
from ..models.usuario_model import Usuario
from rol.models import Rol
from django.contrib.auth.password_validation import validate_password
import random
import string
from utils.email_utils import enviar_correo_bienvenida_empleado


class UsuarioSerializer(serializers.ModelSerializer):
    rol_id_out = serializers.SerializerMethodField(read_only=True)
    rol_id = serializers.PrimaryKeyRelatedField(queryset=Rol.objects.all())

    class Meta:
        model = Usuario
        fields = ['id', 'username', 'password', 'nombre', 'apellido', 'correo', 'estado', 'rol_id', 'rol_id_out','tipo_documento', 'numero_documento']
        # Hacer que la contraseña solo se pueda escribir y no leer
        extra_kwargs = {
            'password': {'write_only': True, 'required': False},
            'username': {
              'error_messages': {
                'unique': 'Ya existe un usuario con ese nombre de usuario.',
                'required': 'El nombre de usuario es obligatorio.'
              }
            },
            'correo': {
              'error_messages': {
                 'unique': 'Ya existe un usuario con ese correo electrónico.',
                 'required': 'El correo electrónico es obligatorio.'
               }
            },
            'numero_documento': {
              'error_messages': {
                 'unique': 'Ya existe un usuario con ese número de documento.'
               }
            }
        }

    def get_rol_id_out(self, obj):
        return obj.rol_id.nombre if obj and obj.rol_id else None

    def validate_rol_id(self, rol_id):
        # Verifica que el rol exista
        try:
            Rol.objects.get(id=rol_id.id)
        except Rol.DoesNotExist:
            raise serializers.ValidationError("El rol no existe")
        return rol_id

    def validate_estado(self, estado):
        # Valida que el estado sea uno de los permitidos
        estados_validos = [choice[0] for choice in Usuario.ESTADOS_CHOICES]
        if estado not in estados_validos:
            raise serializers.ValidationError(f"Estado no válido. Opciones permitidas: {estados_validos}")
        return estado

    def validate_password(self, password):
        # Valida la fortaleza de la contraseña solo si está presente
        if password:
            try:
                validate_password(password)
            except Exception as e:
                raise serializers.ValidationError(str(e))
        return password
    
    def generar_contrasena_segura_usuario(longitud=12):
        caracteres = string.ascii_letters + string.digits
        especiales = "!@#$%^&*()_+-=[]{}|;:,.<>?/~"

        contrasena = [
          random.choice(string.ascii_lowercase),
          random.choice(string.ascii_uppercase),
          random.choice(string.digits),
          random.choice(especiales),
        ]

        restante = longitud - len(contrasena)
        contrasena += random.choices(caracteres + especiales, k=restante)

        random.shuffle(contrasena)
        return ''.join(contrasena)

    def create(self, validated_data):

        password = validated_data.pop('password', None)
        correo = validated_data.get('correo')
        nombre = validated_data.get('nombre')
        rol_obj = validated_data.get('rol_id')
        rol_nombre = rol_obj.nombre if rol_obj else "usuario"

        if not password:
           password = UsuarioSerializer.generar_contrasena_segura_usuario()

        instance = Usuario(**validated_data)
        instance.set_password(password)
        instance.save()

        enlace_cambio_password = f"http://localhost:5173/cambiar-password?usuario={instance.id}"

        enviar_correo_bienvenida_empleado(
          destinatario=correo,
          nombre_empleado=nombre,
          contrasena=password,
          enlace_cambio_password=enlace_cambio_password,
          rol_usuario=rol_nombre
        )

        return instance

    def update(self, instance, validated_data):
        # Elimina el campo password de los datos validados si no está presente
        password = validated_data.pop('password', None)

        # Si se proporciona una nueva contraseña, se actualiza
        if password:
            instance.set_password(password)

        # Actualiza los demás campos
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance