from django.urls import path

from . import views

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('inventory/', views.inventory_view, name='inventory'),
    path('pos/', views.pos_view, name='pos'),
    path('hr/', views.hr_view, name='hr'),
    path('reports/', views.reports_view, name='reports'),
]
