from django.db import models

# ── MODELO 1: Mesa ──────────────────────────────
class Mesa(models.Model):
    numero = models.IntegerField(unique=True)
    capacidad = models.IntegerField()
    disponible = models.BooleanField(default=True)

    def __str__(self):
        return f"Mesa {self.numero}"

# ── MODELO 2: Producto (menú) ────────────────────
class Producto(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    disponible = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre

# ── MODELO 3: Pedido ─────────────────────────────
class Pedido(models.Model):
    ESTADOS = [
        ('activo', 'Activo'),
        ('facturado', 'Facturado'),
        ('cancelado', 'Cancelado'),
    ]
    # ForeignKey = "un pedido pertenece a una mesa" (regla de negocio)
    mesa = models.ForeignKey(Mesa, on_delete=models.CASCADE, related_name='pedidos')
    productos = models.ManyToManyField(Producto)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='activo')
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Pedido {self.id} - Mesa {self.mesa.numero}"