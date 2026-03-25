from django.urls import path
from . import views

urlpatterns = [
    path('', views.vista_login, name='login_html'),
    path('mesas/', views.vista_mesas, name='mesas_html'),
    path('productos/', views.vista_productos, name='productos_html'),
    path('pedidos/', views.vista_pedidos, name='pedidos_html'),
]