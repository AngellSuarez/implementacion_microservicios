from rest_framework import serializers
from .models import Servicio
import requests
import os

class ServicioSerializer(serializers.ModelSerializer):
    imagen = serializers.ImageField(
        write_only=True,
        required=False,
        error_messages={
            'invalid_image': 'Sube una imagen válida. El archivo que subiste no es una imagen.'
        }
    )
    class Meta:
        model = Servicio
        fields = '__all__'  

    def validate_nombre(self, nombre):
        if not nombre:
            raise serializers.ValidationError("El nombre es requerido")
        if len(nombre) < 3:
            raise serializers.ValidationError("El nombre debe tener al menos 3 caracteres")
        if nombre.isdigit():
            raise serializers.ValidationError("El nombre no puede contener solo números")
        return nombre
    
    def validate_duracion(self, duracion):
        if duracion.total_seconds() <= 0:
           raise serializers.ValidationError("La duración debe ser mayor a 0.")
        return duracion

    def validate_precio(self, precio):
        if precio is None:
            raise serializers.ValidationError("El precio es requerido")
        if precio < 0:
            raise serializers.ValidationError("El precio no puede ser negativo")
        return precio

    def validate_tipo(self, tipo):
        tipo_choices = [choice[0] for choice in Servicio.TIPO_CHOICES]
        if tipo not in tipo_choices:
            raise serializers.ValidationError(f"Tipo no válido, opciones válidas: {tipo_choices}")
        return tipo

    def validate_estado(self, estado):
        estado_choices = [choice[0] for choice in Servicio.ESTADOS_CHOICES]
        if not estado:
            raise serializers.ValidationError("El estado es requerido")
        if estado not in estado_choices:
            raise serializers.ValidationError(f"Estado no válido, opciones válidas: {estado_choices}")
        return estado

    def create(self, validated_data):
        imagen = validated_data.pop('imagen', None)
        if imagen:
            validated_data['url_imagen'] = self._subir_imagen_imgbb(imagen)
        else:
            validated_data['url_imagen'] = "https://i.ibb.co/zWhfbh8/default.jpg"  # URL por defecto

        return super().create(validated_data)

    def update(self, instance, validated_data):
        imagen = validated_data.pop('imagen', None)
        if imagen:
            validated_data['url_imagen'] = self._subir_imagen_imgbb(imagen)
        return super().update(instance, validated_data)

    def _subir_imagen_imgbb(self, imagen):
        """Sube la imagen a ImgBB y devuelve la URL."""
        IMGBB_API_KEY = os.getenv('IMGBB_API_KEY')
        if not IMGBB_API_KEY:
            return "https://i.ibb.co/zWhfbh8/default.jpg"

        url = "https://api.imgbb.com/1/upload"
        files = {"image": imagen}
        payload = {"key": IMGBB_API_KEY}

        try:
            response = requests.post(url, files=files, data=payload)
            response.raise_for_status()
            return response.json().get("data", {}).get("url", "https://i.ibb.co/zWhfbh8/default.jpg")
        except requests.exceptions.RequestException:
            return "https://i.ibb.co/zWhfbh8/default.jpg"
        
    def validate(self, data):
     if self.instance is None:
        # Solo para creación
        if 'imagen' not in self.initial_data or not self.initial_data['imagen']:
            raise serializers.ValidationError({"imagen": "La imagen es obligatoria."})
     return data