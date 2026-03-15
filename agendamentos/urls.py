from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.index, name='index'),
    path('novo/', views.novo_agendamento, name='novo_agendamento'),
    path('editar/<int:pk>/', views.editar_agendamento, name='editar_agendamento'),
    path('excluir/<int:pk>/', views.excluir_agendamento, name='excluir_agendamento'),
    path('paciente/novo/', views.novo_paciente, name='novo_paciente'),
    path('concluir/<int:pk>/', views.concluir_agendamento, name='concluir_agendamento'),
    path('relatorio/pdf/', views.gerar_relatorio_pdf, name='gerar_relatorio_pdf'),
    path('dentista/novo/', views.novo_dentista, name='novo_dentista'),
    path('pacientes/', views.lista_pacientes, name='lista_pacientes'),
    path('paciente/editar/<int:pk>/', views.editar_paciente, name='editar_paciente'),
    path('paciente/excluir/<int:pk>/', views.excluir_paciente, name='excluir_paciente'),
    # Rota de Login e Logout
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('registrar/', views.registrar, name='registrar'),
    path('perfil/', views.perfil, name='perfil'),
]