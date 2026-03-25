# 📋 GUÍA DE RESPUESTAS - ENTREVISTA TÉCNICA API
## Restaurante SENA Tolimense

---

## ✅ PREGUNTA 1: CREAR UN RECURSO CON THUNDER CLIENT

### 📍 Ubicación del Código
- **Endpoint**: `/api/productos/`
- **Archivo**: `restaurante/views.py` (ProductoViewSet)
- **Serializer**: `restaurante/serializers.py` (ProductoSerializer)

### 🎯 PASO A PASO: Crear un Producto

#### 1️⃣ **Prerequisito: Obtener Token**

**Endpoint**: `POST http://127.0.0.1:8000/api/auth/login/`

**Headers:**
```
Content-Type: application/json
```

**Body (JSON):**
```json
{
  "username": "admin",
  "password": "123456"
}
```

**Respuesta:**
```json
{
  "token": "a7f8c2d9e1b4a6f3h5j7k9l2m4n6p8q0",
  "user": {
    "id": 1,
    "username": "admin",
    "email": "admin@restaurante.com"
  }
}
```

#### 2️⃣ **Crear el Recurso (Producto)**

**Endpoint**: `POST http://127.0.0.1:8000/api/productos/`

**Headers:**
```
Content-Type: application/json
Authorization: Token a7f8c2d9e1b4a6f3h5j7k9l2m4n6p8q0
```

**Body (JSON):**
```json
{
  "nombre": "Arepa de Queso",
  "descripcion": "Arepa caliente con queso derretido",
  "precio": 8500.00,
  "disponible": true
}
```

#### 3️⃣ **Respuesta del Servidor (HTTP 201 Created)**

```json
{
  "id": 15,
  "nombre": "Arepa de Queso",
  "descripcion": "Arepa caliente con queso derretido",
  "precio": 8500.00,
  "disponible": true,
  "fecha_creacion": "2026-03-25T14:30:45.123456Z"
}
```

### 📌 Lo que sucede internamente:

1. **Autenticación**: DRF verifica el token en el header `Authorization`
2. **Validación**: ProductoSerializer valida que:
   - `precio > 0` (ver línea 45 en serializers.py)
   - `nombre` no esté vacío
3. **Guardado**: Se crea un registro en la tabla `restaurante_producto`
4. **Respuesta**: Retorna HTTP 201 con los datos creados + ID auto-generado

---

## ✅ PREGUNTA 2: SIN TOKEN - ¿QUÉ PASA?

### 🎯 PASO A PASO: Llamar sin Token

#### 1️⃣ **Mismo Endpoint SIN el Header Authorization**

**Endpoint**: `POST http://127.0.0.1:8000/api/productos/`

**Headers:**
```
Content-Type: application/json
```

**Body (JSON):**
```json
{
  "nombre": "Ajiaco Tolimense",
  "descripcion": "Sopa típica del Tolima",
  "precio": 12000.00,
  "disponible": true
}
```

#### 2️⃣ **Respuesta del Servidor (HTTP 401 Unauthorized)**

```json
{
  "detail": "Authentication credentials were not provided."
}
```

### 📌 ¿Por qué sucede esto?

**Ubicación**: `config/settings.py` (líneas 145-150)

```python
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',  # ← REQUIERE TOKEN
    ],
}
```

**Explicación:**
- `IsAuthenticated` → Solo usuarios autenticados pueden acceder
- Sin token en headers → Django REST Framework rechaza la solicitud
- Respuesta: `HTTP 401 Unauthorized` + mensaje de error

**Excepción**: Los endpoints de autenticación (`/api/auth/registro/` y `/api/auth/login/`) NO requieren token.

---

## ✅ PREGUNTA 3: REGLAS DE NEGOCIO ESPECIALES

### 🎯 REGLA #1: Una Mesa Solo Pueda Tener UN Pedido Activo

#### 📍 Ubicación del Código
**Archivo**: `restaurante/serializers.py` (Líneas 92-112)

#### 📝 Código Completo:

```python
class PedidoSerializer(serializers.ModelSerializer):
    total_con_iva = serializers.SerializerMethodField()
    
    class Meta:
        model = Pedido
        fields = ['id', 'mesa', 'productos', 'estado', 'total', 'total_con_iva', 'fecha']

    def get_total_con_iva(self, obj):
        """Calcula el total con IVA del 19%"""
        return round(float(obj.total) * 1.19, 2)

    def validate(self, data):
        """Validación: Una mesa no puede tener dos pedidos activos"""
        mesa = data.get('mesa')
        
        # Busca pedidos activos en esa mesa
        pedidos_activos = Pedido.objects.filter(
            mesa=mesa,
            estado='activo'
        )
        
        # Si estamos editando, excluye el pedido actual
        if self.instance:
            pedidos_activos = pedidos_activos.exclude(pk=self.instance.pk)
        
        # Si hay pedidos activos, lanza error
        if pedidos_activos.exists():
            raise serializers.ValidationError(
                "Esta mesa ya tiene un pedido activo. "
                "Debe facturarlo o cancelarlo primero."
            )
        
        return data
```

#### 🧪 PRUEBA PRÁCTICA: Intenta Crear Dos Pedidos en la Misma Mesa

**1️⃣ Crear Primer Pedido (Mesa 1)**

**Endpoint**: `POST http://127.0.0.1:8000/api/pedidos/`

**Headers:**
```
Content-Type: application/json
Authorization: Token <tu_token>
```

**Body:**
```json
{
  "mesa": 1,
  "productos": [1, 2],
  "estado": "activo",
  "total": 25000.00
}
```

**Respuesta**: ✅ HTTP 201 Created

---

**2️⃣ Intenta Crear Segundo Pedido en la MISMA Mesa (Mesa 1)**

**Endpoint**: `POST http://127.0.0.1:8000/api/pedidos/`

**Headers:**
```
Content-Type: application/json
Authorization: Token <tu_token>
```

**Body:**
```json
{
  "mesa": 1,
  "productos": [3],
  "estado": "activo",
  "total": 8500.00
}
```

**Respuesta**: ❌ HTTP 400 Bad Request

```json
{
  "non_field_errors": [
    "Esta mesa ya tiene un pedido activo. Debe facturarlo o cancelarlo primero."
  ]
}
```

---

### 🎯 REGLA #2: Cálculo Automático de IVA (19%)

#### 📍 Ubicación del Código
**Archivo**: `restaurante/serializers.py` (Líneas 100-103)

```python
total_con_iva = serializers.SerializerMethodField()

def get_total_con_iva(self, obj):
    """Calcula el total con IVA del 19%"""
    return round(float(obj.total) * 1.19, 2)
```

#### 📝 Ejemplo:
- **Total**: $25,000
- **IVA (19%)**: $4,750
- **Total con IVA**: $29,750

**Cómo Verlo en la Respuesta:**

**Endpoint**: `GET http://127.0.0.1:8000/api/pedidos/1/`

**Respuesta:**
```json
{
  "id": 1,
  "mesa": 1,
  "productos": [1, 2],
  "estado": "activo",
  "total": 25000.00,
  "total_con_iva": 29750.00,  ← CALCULADO AUTOMÁTICAMENTE
  "fecha": "2026-03-25T14:30:45.123456Z"
}
```

---

### 🎯 REGLA #3: Validaciones en Campos Específicos

#### 📍 Ubicación
**Archivo**: `restaurante/serializers.py`

#### 1. **Número de Mesa must be > 0**
```python
# Línea 28-32
def validate_numero(self, value):
    if value <= 0:
        raise serializers.ValidationError(
            "El número de mesa debe ser mayor a 0."
        )
    return value
```

#### 2. **Capacidad entre 1-20 personas**
```python
# Línea 34-40
def validate_capacidad(self, value):
    if value < 1 or value > 20:
        raise serializers.ValidationError(
            "La capacidad debe estar entre 1 y 20 personas."
        )
    return value
```

#### 3. **Precio del Producto > 0**
```python
# Línea 60-64
def validate_precio(self, value):
    if value <= 0:
        raise serializers.ValidationError(
            "El precio debe ser mayor a $0."
        )
    return value
```

#### 🧪 PRUEBA: Crear Mesa con Capacidad Inválida

**Endpoint**: `POST http://127.0.0.1:8000/api/mesas/`

**Body:**
```json
{
  "numero": 5,
  "capacidad": 25,  ← INVÁLIDO (máximo 20)
  "disponible": true
}
```

**Respuesta**: ❌ HTTP 400

```json
{
  "capacidad": [
    "La capacidad debe estar entre 1 y 20 personas."
  ]
}
```

---

## ✅ PREGUNTA EXTRA: DIFERENCIA SERIALIZER vs FORMULARIO DJANGO PURO

### 📍 Ubicación

**Serializer**: `restaurante/serializers.py`
**Formulario Django Puro**: No existe en este proyecto, pero aquí está la comparación:

### 📊 Tabla Comparativa

| Aspecto | **Serializer DRF** | **Formulario Django** |
|---------|-------------------|----------------------|
| **Propósito** | Convertir datos <→ JSON (APIs) | Renderizar HTML form |
| **Entrada** | JSON (desde cliente) | Datos de formulario HTML |
| **Salida** | JSON (al cliente) | HTML renderizado |
| **Validación** | `validate_campo()` + `validate()` | `clean_campo()` + `clean()` |
| **Ubicación** | `serializers.py` | `forms.py` |
| **Uso** | APIs REST | Templates HTML |
| **Respuesta Error** | JSON estructurado | HTML con errores |

### 🔍 EJEMPLO EN TU CÓDIGO

**Con Serializer (API):**

```python
# En serializers.py
class ProductoSerializer(serializers.ModelSerializer):
    def validate_precio(self, value):
        if value <= 0:
            raise serializers.ValidationError("Precio inválido")
        return value
        
    class Meta:
        model = Producto
        fields = ['nombre', 'descripcion', 'precio', 'disponible']
```

**Con Formulario Django (HTML):**

```python
# En forms.py (NO EXISTE EN TU PROYECTO, pero así sería)
from django import forms
from .models import Producto

class ProductoForm(forms.ModelForm):
    def clean_precio(self):
        precio = self.cleaned_data.get('precio')
        if precio <= 0:
            raise forms.ValidationError("Precio inválido")
        return precio
    
    class Meta:
        model = Producto
        fields = ['nombre', 'descripcion', 'precio', 'disponible']
```

### ✅ ¿Por qué tu proyecto usa Serializers?

Porque es una **API REST** (no un sitio web tradicional):
- Recibe JSON desde JavaScript del navegador
- Retorna JSON para que el JavaScript lo procese
- No necesita renderizar HTML en el servidor

---

## 🔒 BONUS: FLUJO COMPLETO REGISTRO → LOGIN → API

### 📍 Ubicación de Autenticación
**Archivo**: `restaurante/views.py` (Líneas 18-80)

### 🎯 PASO A PASO

#### 1️⃣ **REGISTRO**

**Endpoint**: `POST http://127.0.0.1:8000/api/auth/registro/`

```json
{
  "username": "nuevo_usuario",
  "email": "nuevo@restaurante.com",
  "password": "ContraseñaSegura123"
}
```

**Respuesta: HTTP 201**
```json
{
  "token": "abc123def456ghi789jkl012",
  "user": {
    "id": 5,
    "username": "nuevo_usuario",
    "email": "nuevo@restaurante.com"
  }
}
```

**¿Qué sucede?**
1. Se crea un nuevo usuario en `auth_user`
2. Se crea un Token único asociado al usuario
3. Se retorna el token

---

#### 2️⃣ **LOGIN**

**Endpoint**: `POST http://127.0.0.1:8000/api/auth/login/`

```json
{
  "username": "nuevo_usuario",
  "password": "ContraseñaSegura123"
}
```

**Respuesta: HTTP 200**
```json
{
  "token": "abc123def456ghi789jkl012",
  "user": {
    "id": 5,
    "username": "nuevo_usuario",
    "email": "nuevo@restaurante.com"
  }
}
```

**¿Qué sucede?**
1. Se valida username + password
2. Se busca el Token existente del usuario
3. Se retorna el mismo token

---

#### 3️⃣ **USAR EL TOKEN EN PETICIONES**

**Endpoint**: `GET http://127.0.0.1:8000/api/mesas/`

**Headers:**
```
Authorization: Token abc123def456ghi789jkl012
```

**Respuesta: HTTP 200**
```json
[
  {
    "id": 1,
    "numero": 1,
    "capacidad": 4,
    "disponible": true
  },
  {
    "id": 2,
    "numero": 2,
    "capacidad": 6,
    "disponible": false
  }
]
```

**¿Qué sucede?**
1. DRF busca el token en el header `Authorization`
2. Valida que existe en la tabla `authtoken_token`
3. Si es válido → permite acceso
4. Si no → retorna HTTP 401

---

## 🔍 ¿DÓNDE SE GUARDA EL TOKEN?

### 📍 Ubicación en Base de Datos

**Tabla**: `authtoken_token`

```sql
SELECT * FROM authtoken_token;
```

**Estructura:**
```
┌────┬──────────────────────────────────────┬──────────────────────┐
│ id │ key                                  │ user_id              │
├────┼──────────────────────────────────────┼──────────────────────┤
│ 1  │ abc123def456ghi789jkl012     │ 5                    │
│ 2  │ xyz789uvw456rst123qwerty     │ 3                    │
└────┴──────────────────────────────────────┴──────────────────────┘
```

**Relación:**
- Cada usuario en `auth_user` tiene un único token en `authtoken_token`
- El token está vinculado al usuario por `user_id` (Foreign Key)

**Cómo se genera:**

En `views.py` (Línea 32):
```python
from rest_framework.authtoken.models import Token

def vista_registro(request):
    # ... crear usuario ...
    token, created = Token.objects.get_or_create(user=user)
    return Response({'token': token.key})
```

---

## 📱 DEMOSTRACIÓN EN VIVO CON THUNDER CLIENT

### Comando Rápido para Copiar/Pegar:

```
1. POST http://127.0.0.1:8000/api/auth/login/
   Body: {"username":"admin","password":"123456"}
   
2. Copiar token de la respuesta
   
3. POST http://127.0.0.1:8000/api/productos/
   Header: Authorization: Token <tu_token>
   Body: {"nombre":"Tamal Tolimense","precio":5000,"descripcion":"Delicioso","disponible":true}
   
4. Intentar sin Header → HTTP 401
```

---

## 🎓 RESPUESTAS CORTAS PARA LA ENTREVISTA

### P: "¿Dónde está la regla de que una mesa solo tenga un pedido activo?"
**R:** "En el serializer de Pedido (`restaurante/serializers.py`, método `validate` en líneas 92-112). Valida contra la base de datos y lanza un error 400 si ya existe un pedido activo."

### P: "¿Qué tipo de autenticación usas?"
**R:** "Token-based, usando `rest_framework.authtoken`. El token se genera en registro/login y se valida en cada petición usando el header `Authorization`."

### P: "¿Qué pasa si no envío el token?"
**R:** "Django REST Framework retorna HTTP 401 con el mensaje 'Authentication credentials were not provided.' porque tengo `DEFAULT_PERMISSION_CLASSES: IsAuthenticated` en settings."

### P: "¿Cómo creas un recurso?"
**R:** "Con POST al endpoint `/api/productos/` (o mesas/pedidos). Incluyo un token en el header, envío JSON valido y retorna HTTP 201 con el recurso creado."

---

**✅ ¡Listo para tu entrevista!**
