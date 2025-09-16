from rest_framework import serializers
from ..models import Permiso_Rol, Permiso, Rol

class PermisoRolSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permiso_Rol;
        fields = '__all__';
        
        def validate(self,data):
            rol_id = data.get('rol_id');
            permiso_id = data.get('permiso_id');
            
            if not Rol.objects.filter(id=rol_id).exists():
                raise serializers.ValidationError("El rol no existe");
            if not Permiso.objects.filter(id=permiso_id).exists():
                raise serializers.ValidationError("El permiso no existe");
            
            return data;