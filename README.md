# 🍽️ Sistema de Restaurante Tolimense
**SENA — Análisis y Desarrollo de Software 228185**  
Grupo 4 | Taller Evaluativo Final

## Integrantes
- Nuñez Orjuela Jorlin Javier
- Marin Chaguala Yeison Jobany
- Arias Quiroga Nicolas

## Tecnologías
- Python 3.13 / Django 6.0
- Django REST Framework 3.17
- PostgreSQL (Supabase)
- Bootstrap 5

## Modelos
- **Mesa**: número, capacidad, disponible
- **Producto**: nombre, descripción, precio, disponible
- **Pedido**: mesa (FK), productos (M2M), estado, total, fecha

## Reglas de negocio
- Una mesa no puede tener dos pedidos activos simultáneamente
- Al facturar se calcula automáticamente el total + IVA del 19%

## Instalación

### 1. Clonar el repositorio
```bash
git clone https://github.com/YeisonDV/restaurante-sena.git
cd restaurante-sena
```

### 2. Crear entorno virtual
```bash
python -m venv env
env\Scripts\activate
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Crear archivo .env
Crea un archivo `.env` en la raíz con estas variables:
```
SECRET_KEY=tu-secret-key-aqui
DEBUG=True
DATABASE_URL=postgresql://postgres:[PASSWORD]@db.xxxx.supabase.co:5432/postgres
```

### 5. Aplicar migraciones
```bash
python manage.py migrate
```

### 6. Crear superusuario (opcional)
```bash
python manage.py createsuperuser
```

### 7. Correr el servidor
```bash
python manage.py runserver
```

Abre el navegador en `http://127.0.0.1:8000/`

## Endpoints de la API

| Método | URL | Descripción | Auth |
|--------|-----|-------------|------|
| POST | /api/auth/registro/ | Registro de usuario | No |
| POST | /api/auth/login/ | Login → token | No |
| POST | /api/auth/logout/ | Cerrar sesión | 🔒 |
| GET | /api/mesas/ | Listar mesas | 🔒 |
| POST | /api/mesas/ | Crear mesa | 🔒 |
| PUT | /api/mesas/{id}/ | Actualizar mesa | 🔒 |
| DELETE | /api/mesas/{id}/ | Eliminar mesa | 🔒 |
| GET | /api/productos/ | Listar productos | 🔒 |
| POST | /api/productos/ | Crear producto | 🔒 |
| GET | /api/pedidos/ | Listar pedidos | 🔒 |
| POST | /api/pedidos/ | Crear pedido | 🔒 |
| PATCH | /api/pedidos/{id}/ | Facturar pedido | 🔒 |

🔒 Requiere header: `Authorization: Token <tu-token>`

## Vistas HTML
- `/` — Login
- `/mesas/` — Gestión de mesas
- `/productos/` — Menú de productos
- `/pedidos/` — Gestión de pedidos con facturación