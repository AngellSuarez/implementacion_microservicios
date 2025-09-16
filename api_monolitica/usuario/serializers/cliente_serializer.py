from rest_framework import serializers
from ..models.usuario_model import Usuario
from ..models.cliente_model import Cliente
from rol.models import Rol
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ObjectDoesNotExist

import random
import string
from utils.email_utils import enviar_correo_bienvenida_cliente
from django.conf import settings


class ClienteSerializer(serializers.ModelSerializer):
    username = serializers.CharField(write_only=True, required=False)
    password = serializers.CharField(write_only=True, required=False)

    # Salida
    username_out = serializers.SerializerMethodField(read_only=True)
    rol_id_out = serializers.SerializerMethodField(read_only=True)
    usuario_id = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Cliente
        fields = [
            'username', 'password',
            'nombre', 'apellido', 'tipo_documento', 'numero_documento',
            'correo', 'celular', 'estado',
            'username_out', 'rol_id_out', 'usuario_id'
        ]
        extra_kwargs = {
            'username': {
              'error_messages': {
                'unique': 'Ya existe un cliente con ese nombre de usuario.',
                'required': 'El nombre de usuario de cliente es obligatorio.'
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
                 'unique': 'Ya existe un cliente con ese número de documento.'
               }
            }
        }
        
        
    def validate_username(self, username):
        instance = getattr(self, 'instance', None)
        usuario_id = instance.usuario.pk if instance and hasattr(instance, 'usuario') else None

        if Usuario.objects.exclude(pk=usuario_id).filter(username=username).exists():
           raise serializers.ValidationError("El nombre de usuario ya está en uso.")

        if len(username) < 4:
           raise serializers.ValidationError("El nombre de usuario debe tener al menos 4 caracteres.")

        if ' ' in username:
           raise serializers.ValidationError("El nombre de usuario no puede contener espacios.")

        return username


    def get_username_out(self, obj):
        return obj.usuario.username if obj.usuario else None

    def get_rol_id_out(self, obj):
        return obj.usuario.rol_id.id if obj.usuario and obj.usuario.rol_id else None

    def get_usuario_id(self, obj):
        return obj.usuario.id if obj.usuario else None

    def validate_estado(self, estado):
        estados_validos = [choice[0] for choice in Cliente.ESTADOS_CHOICES]
        if estado not in estados_validos:
            raise serializers.ValidationError(f"Estado no válido, las opciones son: {estados_validos}")
        return estado

    def validate_tipo_documento(self, tipo_documento):
        tipos_validos = [choice[0] for choice in Cliente.TIPO_DOCUMENTO_CHOICES]
        if tipo_documento not in tipos_validos:
            raise serializers.ValidationError(f"Tipo de documento no válido, las opciones son: {tipos_validos}")
        return tipo_documento

    def validate_numero_documento(self, numero_documento):
        instance = getattr(self, 'instance', None)
        if Cliente.objects.exclude(pk=instance.pk if instance else None).filter(numero_documento=numero_documento).exists():
            raise serializers.ValidationError("El número de documento ya está registrado")
        return numero_documento

    def validate_correo(self, correo):
        instance = getattr(self, 'instance', None)
        usuario_id = instance.usuario.pk if instance and hasattr(instance, 'usuario') else None
        if Cliente.objects.exclude(pk=instance.pk if instance else None).filter(correo=correo).exists():
            raise serializers.ValidationError("El correo ya está registrado en cliente")
        if Usuario.objects.exclude(pk=usuario_id).filter(correo=correo).exists():
            raise serializers.ValidationError("El correo ya está registrado en usuario")
        return correo

    def validate_nombre(self, nombre):
        if not nombre or len(nombre) < 3 or nombre.isdigit():
            raise serializers.ValidationError("El nombre debe tener al menos 3 caracteres y no ser solo números")
        return nombre

    def validate_apellido(self, apellido):
        if not apellido or len(apellido) < 3 or apellido.isdigit():
            raise serializers.ValidationError("El apellido debe tener al menos 3 caracteres y no ser solo números")
        return apellido
    
    def generar_contrasena_segura_cliente(longitud=8):
        caracteres = string.ascii_letters + string.digits
        especiales = "!@#$%^&*()_+-=[]{}|;:,.<>?/~"

        # Asegurar al menos un carácter especial
        contrasena = [
           random.choice(string.ascii_lowercase),
           random.choice(string.ascii_uppercase),
           random.choice(string.digits),
           random.choice(especiales),
        ]

        # Completar el resto de la contraseña
        restante = longitud - len(contrasena)
        contrasena += random.choices(caracteres + especiales, k=restante)

        # Mezclar los caracteres
        random.shuffle(contrasena)
        return ''.join(contrasena)

    def create(self, validated_data):
        username = validated_data.pop('username')
    
        # Si ya viene una contraseña (desde el register), úsala; si no, genera una
        password = validated_data.pop('password', None)
        if not password:
           password = ClienteSerializer.generar_contrasena_segura_cliente()

        correo = validated_data.get('correo')
        nombre = validated_data.get('nombre', '')
        apellido = validated_data.get('apellido', '')

        try:
           rol_cliente = Rol.objects.get(nombre__iexact="cliente")
        except ObjectDoesNotExist:
           raise serializers.ValidationError("No se encontró el rol 'cliente' en la base de datos.")

        usuario = Usuario.objects.create_user(
          username=username,
          password=password,
          rol_id=rol_cliente,
          correo=correo,
          nombre=nombre,
          apellido=apellido
        )
        
        enlace_cambio_password = f"http://localhost:5173/cambiar-password?usuario={usuario.id}"
        
        enviar_correo_bienvenida_cliente(
          destinatario=correo,
          nombre_cliente=nombre,
          contrasena=password,
          enlace_cambio_password=enlace_cambio_password
        )

        # Elimina cualquier campo no relacionado antes de crear el Cliente
        validated_data.pop('password', None)
        validated_data.pop('username', None)

        cliente = Cliente.objects.create(usuario=usuario, **validated_data)
        return cliente


    def update(self, instance, validated_data):
        usuario = instance.usuario
        username = validated_data.pop('username', None)
        password = validated_data.pop('password', None)

        # Reforzar que mantenga el rol cliente si quieres evitar cambios
        try:
            rol_cliente = Rol.objects.get(nombre__iexact="cliente")
        except ObjectDoesNotExist:
            raise serializers.ValidationError("No se encontró el rol 'cliente' en la base de datos.")

        if username is not None:
            usuario.username = username
        if password is not None:
            usuario.set_password(password)

        usuario.rol_id = rol_cliente

        # Campos compartidos
        for field in ['nombre', 'apellido', 'correo']:
            if field in validated_data:
                setattr(usuario, field, validated_data.get(field))

        usuario.save()

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save(force_update=True)

        return instance