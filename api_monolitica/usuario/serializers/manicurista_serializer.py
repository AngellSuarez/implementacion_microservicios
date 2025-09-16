from rest_framework import serializers
from ..models.usuario_model import Usuario
from ..models.manicurista_model import Manicurista
from rol.models import Rol
from django.contrib.auth.password_validation import validate_password

import random
import string
from utils.email_utils import enviar_correo_bienvenida_manicurista  
from django.conf import settings

class ManicuristaSerializer(serializers.ModelSerializer):
    # Campos para escritura
    username = serializers.CharField(write_only=True,required = False)
    password = serializers.CharField(write_only=True, required = False)
    
    # Campos para lectura
    username_out = serializers.SerializerMethodField(read_only=True)
    rol_id_out = serializers.SerializerMethodField(read_only=True)
    usuario_id = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Manicurista
        fields = [
            'username', 'password',
            'nombre', 'apellido', 'tipo_documento', 'numero_documento',
            'correo', 'celular', 'estado', 'fecha_nacimiento', 'fecha_contratacion',
            'username_out', 'rol_id_out','usuario_id'
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

    def get_username_out(self, obj):
        return obj.usuario.username if obj.usuario else None

    def get_rol_id_out(self, obj):
        return obj.usuario.rol_id.id if obj.usuario and obj.usuario.rol_id else None
    
    def get_usuario_id(self, obj):
        return obj.usuario.id if obj.usuario else None
    
    
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
    
    def validate_estado(self, estado):
        estados_validos = [choice[0] for choice in Manicurista.ESTADOS_CHOICES]
        if estado not in estados_validos:
            raise serializers.ValidationError(f"Estado no valido, las opciones son: {estados_validos}")
        return estado

    def validate_tipo_documento(self, tipo):
        tipos_validos = [choice[0] for choice in Manicurista.TIPO_DOCUMENTO_CHOICES]
        if tipo not in tipos_validos:
            raise serializers.ValidationError(f"Tipo de documento no valido, las opciones son: {tipos_validos}")
        if not tipo:
            raise serializers.ValidationError("El tipo no puede estar vacio")
        return tipo

    def validate_numero_documento(self, numero_documento):
        instance = getattr(self, 'instance', None)
        if Manicurista.objects.exclude(pk=instance.pk if instance else None).filter(numero_documento=numero_documento).exists():
            raise serializers.ValidationError("El numero de documento ya existe")
        if not numero_documento:
            raise serializers.ValidationError("El numero de documento no puede estar vacio")
        return numero_documento

    def validate_correo(self, correo):
        queryset = Usuario.objects.filter(correo=correo)

    # Excluir el usuario actual si estás actualizando
        if self.instance and hasattr(self.instance, 'usuario'):
            queryset = queryset.exclude(pk=self.instance.usuario.pk)

        if queryset.exists():
            raise serializers.ValidationError("El correo ya se encuentra registrado")

        if not correo:
            raise serializers.ValidationError("El correo es requerido")

        return correo


    def validate_celular(self, celular):
        instance = getattr(self, 'instance', None)
        if Manicurista.objects.exclude(pk=instance.pk if instance else None).filter(celular=celular).exists():
            raise serializers.ValidationError("El celular ya esta registrado")
        return celular

    def validate_nombre(self, nombre):
        if not nombre:
            raise serializers.ValidationError("El nombre no puede estar en blanco")
        if len(nombre) < 3:
            raise serializers.ValidationError("El nombre no puede tener menos de 3 letras")
        if nombre.isdigit():
            raise serializers.ValidationError("El nombre no puede ser solo numeros")
        return nombre

    def validate_apellido(self, apellido):
        if not apellido:
            raise serializers.ValidationError("El apellido no puede estar vacio")
        if len(apellido) < 3:
            raise serializers.ValidationError("El apellido no puede tener menos de 3 letras")
        if apellido.isdigit():
            raise serializers.ValidationError("El apellido no puede ser solo numeros")
        return apellido

    def validate(self, data):
        if 'fecha_contratacion' in data and 'fecha_nacimiento' in data:
            if data['fecha_contratacion'] < data['fecha_nacimiento']:
                raise serializers.ValidationError("La fecha de contrato no debe ser menor a la fecha de nacimiento")
        return data
    
    def generar_contrasena_segura(longitud=8):
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

        password = ManicuristaSerializer.generar_contrasena_segura()

        correo = validated_data.get('correo')
        nombre = validated_data.get('nombre', '')
        apellido = validated_data.get('apellido', '')

        try:
            rol_manicurista = Rol.objects.get(nombre__iexact='manicurista')
        except Rol.DoesNotExist:
            raise serializers.ValidationError("No se encontró el rol 'manicurista' en la base de datos")

        usuario = Usuario.objects.create_user(
            username=username,
            password=password,
            rol_id=rol_manicurista,
            correo=correo,
            nombre=nombre,
            apellido=apellido
        )

        manicurista = Manicurista.objects.create(usuario=usuario, **validated_data)

        enlace_cambio_password = f"{settings.FRONTEND_URL}/cambiar-password"  
        enviar_correo_bienvenida_manicurista(
            destinatario=correo,
            nombre_empleada=f"{nombre} {apellido}",
            contrasena=password,
            enlace_cambio_password=enlace_cambio_password
        )

        return manicurista


    def update(self, instance, validated_data):
        print(f"Datos recibidos para actualizar: {validated_data}")
        print(f"Instancia antes de actualizar - nombre: {instance.nombre}, apellido: {instance.apellido}")

        # Manejar campos de usuario
        usuario = instance.usuario
        username = validated_data.pop('username', None)
        password = validated_data.pop('password', None)
        rol_id = validated_data.pop('rol_id', None)

        if username is not None:
            usuario.username = username
        if password is not None:
            usuario.set_password(password)
        if rol_id is not None:
            usuario.rol_id = rol_id

        # Actualizar campos de usuario y guardar
        usuario_fields = ['nombre', 'apellido', 'correo']
        for field in usuario_fields:
            if field in validated_data:
                setattr(usuario, field, validated_data.get(field))

        usuario.save()
        print(f"Usuario actualizado: {usuario.nombre}, {usuario.apellido}")

        # Actualizar campos de manicurista
        for attr, value in validated_data.items():
            print(f"Actualizando manicurista: {attr} = {value}")
            setattr(instance, attr, value)

        # Intentar diferentes formas de guardar por si acaso
        try:
            instance.save()
            print(f"Instancia después de guardar - nombre: {instance.nombre}, apellido: {instance.apellido}")

            # Forzar recarga desde la base de datos para verificar
            refreshed = Manicurista.objects.get(pk=instance.pk)
            print(f"Verificación desde DB - nombre: {refreshed.nombre}, apellido: {refreshed.apellido}")
        except Exception as e:
            print(f"Error al guardar: {str(e)}")

        return instance