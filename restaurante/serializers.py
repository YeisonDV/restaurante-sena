from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Mesa, Producto, Pedido


# ── SERIALIZER DE USUARIO (registro) ────────────
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        # create_user() hashea la contraseña automáticamente
        user = User.objects.create_user(**validated_data)
        return user


# ── SERIALIZER DE MESA ───────────────────────────
class MesaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mesa
        fields = '__all__'

    # ★ validate_campo() — validación personalizada obligatoria
    def validate_numero(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                "El número de mesa debe ser mayor a 0."
            )
        return value

    def validate_capacidad(self, value):
        if value < 1 or value > 20:
            raise serializers.ValidationError(
                "La capacidad debe estar entre 1 y 20 personas."
            )
        return value


# ── SERIALIZER DE PRODUCTO ───────────────────────
class ProductoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Producto
        fields = '__all__'

    # ★ validate_precio — otra validación personalizada
    def validate_precio(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                "El precio debe ser mayor a $0."
            )
        return value


# ── SERIALIZER DE PEDIDO ─────────────────────────
class PedidoSerializer(serializers.ModelSerializer):

    # Campo calculado: total + IVA 19% (regla de negocio)
    total_con_iva = serializers.SerializerMethodField()

    class Meta:
        model = Pedido
        fields = '__all__'

    def get_total_con_iva(self, obj):
        # obj = la instancia del pedido actual
        return round(float(obj.total) * 1.19, 2)

    # ★ validate() — regla de negocio: mesa sin dos pedidos activos
    def validate(self, data):
        mesa = data.get('mesa')

        if mesa:
            pedidos_activos = Pedido.objects.filter(
                mesa=mesa,
                estado='activo'
            )
            # Si estamos editando, excluimos el pedido actual
            if self.instance:
                pedidos_activos = pedidos_activos.exclude(pk=self.instance.pk)

            if pedidos_activos.exists():
                raise serializers.ValidationError(
                    "Esta mesa ya tiene un pedido activo. "
                    "Debe facturarlo o cancelarlo primero."
                )
        return data