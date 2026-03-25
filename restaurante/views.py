from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from .models import Mesa, Producto, Pedido
from .serializers import (MesaSerializer, ProductoSerializer,
                          PedidoSerializer, UserSerializer)


# ══════════════════════════════════════════════════
#  AUTENTICACIÓN
# ══════════════════════════════════════════════════

@api_view(['POST'])
@permission_classes([AllowAny])  # No requiere token
def registro(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        token, _ = Token.objects.get_or_create(user=user)
        return Response(
            {'token': token.key, 'usuario': serializer.data},
            status=status.HTTP_201_CREATED
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])  # No requiere token para hacer login
def login_view(request):
    username = request.data.get('username')
    password = request.data.get('password')

    user = authenticate(username=username, password=password)

    if user:
        token, _ = Token.objects.get_or_create(user=user)
        return Response({'token': token.key, 'username': user.username})

    return Response(
        {'error': 'Credenciales inválidas'},
        status=status.HTTP_401_UNAUTHORIZED
    )


@api_view(['POST'])
@permission_classes([IsAuthenticated])  # SÍ requiere token
def logout_view(request):
    request.user.auth_token.delete()
    return Response({'mensaje': 'Sesión cerrada correctamente'})


# ══════════════════════════════════════════════════
#  VIEWSETS — CRUD automático
# ══════════════════════════════════════════════════

class MesaViewSet(viewsets.ModelViewSet):
    queryset = Mesa.objects.all()
    serializer_class = MesaSerializer
    permission_classes = [IsAuthenticated]


class ProductoViewSet(viewsets.ModelViewSet):
    queryset = Producto.objects.all()
    serializer_class = ProductoSerializer
    permission_classes = [IsAuthenticated]


class PedidoViewSet(viewsets.ModelViewSet):
    queryset = Pedido.objects.all()
    serializer_class = PedidoSerializer
    permission_classes = [IsAuthenticated]


# ══════════════════════════════════════════════════
#  VISTAS HTML — Templates
# ══════════════════════════════════════════════════
from django.shortcuts import render

def vista_login(request):
    return render(request, 'restaurante/login.html')

def vista_mesas(request):
    return render(request, 'restaurante/mesas.html')

def vista_productos(request):
    return render(request, 'restaurante/productos.html')

def vista_pedidos(request):
    return render(request, 'restaurante/pedidos.html')