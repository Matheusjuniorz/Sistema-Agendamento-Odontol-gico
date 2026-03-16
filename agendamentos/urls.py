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
    path('procedimentos/', views.procedimentos_lista, name='procedimentos_lista'),
    path('procedimentos/novo/', views.procedimento_novo, name='procedimento_novo'),
    path('procedimentos/editar/<int:pk>/', views.procedimento_editar, name='procedimento_editar'),
    path('procedimentos/excluir/<int:pk>/', views.procedimento_excluir, name='procedimento_excluir'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('imprimir-ficha/<int:consulta_id>/', views.imprimir_ficha_consulta, name='imprimir_ficha_consulta'),
    path('dentistas/', views.lista_dentistas, name='lista_dentistas'),
    path('dentistas/editar/<int:pk>/', views.editar_dentista, name='editar_dentista'),
    path('dentistas/excluir/<int:pk>/', views.excluir_dentista, name='excluir_dentista'),
    path('relatorio/pdf/', views.exportar_pdf, name='exportar_pdf'),
    # Rota de Login e Logout
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('registrar/', views.registrar, name='registrar'),
    path('perfil/', views.perfil, name='perfil'),
]