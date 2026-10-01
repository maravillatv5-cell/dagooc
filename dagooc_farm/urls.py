from django.urls import path

from farm_management import views

urlpatterns = [
    path('', views.redirect_to_login, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('inventory/', views.inventory_view, name='inventory'),
    path('pos/', views.pos_view, name='pos'),
    path('hr/', views.hr_view, name='hr'),
    path('hr/attendance/', views.hr_attendance_view, name='hr_attendance'),
    path('hr/payroll/', views.hr_payroll_view, name='hr_payroll'),
    path('hr/applicants/', views.hr_applicants_view, name='hr_applicants'),
    path('hr/employees/', views.hr_employees_view, name='hr_employees'),
    path('reports/', views.reports_view, name='reports'),
    path('applications/', views.applications_view, name='applications'),
    path('tasks/', views.tasks_view, name='tasks'),
]
