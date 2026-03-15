from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Agendamento
from .forms import AgendamentoForm, PacienteForm, DentistaForm, EditarPerfilForm, Paciente
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from .models import Agendamento
from datetime import datetime
from django.contrib.auth import login, authenticate 
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from .models import Paciente


@login_required
def editar_paciente(request, pk):
    paciente = get_object_or_404(Paciente, pk=pk)
    if request.method == "POST":
        form = PacienteForm(request.POST, instance=paciente)
        if form.is_valid():
            form.save()
            return redirect('lista_pacientes')
    else:
        form = PacienteForm(instance=paciente)
    
    return render(request, 'agendamentos/form_paciente.html', {
        'form': form,
        'editando': True,
        'paciente': paciente
    })

# --- VIEW PARA EXCLUIR PACIENTE ---
@login_required
def excluir_paciente(request, pk):
    paciente = get_object_or_404(Paciente, pk=pk)
    
    if request.method == "POST":
        paciente.delete()
        return redirect('lista_pacientes')
        
    return render(request, 'agendamentos/confirmar_exclusao_paciente.html', {
        'paciente': paciente
    })

@login_required
def lista_pacientes(request):
    search = request.GET.get('search')
    if search:
        pacientes = Paciente.objects.filter(nome__icontains=search)
    else:
        pacientes = Paciente.objects.all().order_by('nome')
    
    return render(request, 'agendamentos/lista_pacientes.html', {'pacientes': pacientes})


@login_required
def gerar_relatorio_pdf(request):
    # Cria o objeto de resposta como PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="agenda_consultorio.pdf"'

    # Cria o "palco" para desenhar o PDF
    p = canvas.Canvas(response, pagesize=A4)
    largura, altura = A4

    # Cabeçalho
    p.setFont("Helvetica-Bold", 16)
    p.drawString(100, altura - 50, "🦷 Relatório de Agendamentos - Consultório")
    p.setFont("Helvetica", 10)
    p.drawString(100, altura - 70, f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    
    p.line(100, altura - 80, 500, altura - 80)

    # Títulos da Tabela
    y = altura - 110
    p.setFont("Helvetica-Bold", 11)
    p.drawString(100, y, "Data/Hora")
    p.drawString(220, y, "Paciente")
    p.drawString(380, y, "Dentista")
    p.drawString(480, y, "Status")

    # Conteúdo
    y -= 20
    p.setFont("Helvetica", 10)
    consultas = Agendamento.objects.all().order_by('data_hora')

    for c in consultas:
        if y < 50: # Cria nova página se acabar o espaço
            p.showPage()
            y = altura - 50
        
        p.drawString(100, y, c.data_hora.strftime('%d/%m/%Y %H:%M'))
        p.drawString(220, y, c.paciente.nome[:25]) # Limita nome longo
        p.drawString(380, y, c.dentista.nome[:15])
        p.drawString(480, y, c.status.capitalize())
        y -= 20

    # Finaliza o PDF
    p.showPage()
    p.save()
    return response


@login_required
def index(request):
    busca = request.GET.get('search')
    
    # Base de consultas
    if busca:
        consultas = Agendamento.objects.filter(paciente__nome__icontains=busca).order_by('data_hora')
    else:
        consultas = Agendamento.objects.all().order_by('data_hora')

    # Cálculos para o Dashboard
    # Contamos direto do banco de dados para ser performático
    total_agendados = Agendamento.objects.count()
    total_concluidos = Agendamento.objects.filter(status='concluido').count()
    total_pendentes = Agendamento.objects.filter(status='agendado').count()

    context = {
        'consultas': consultas,
        'total_agendados': total_agendados,
        'total_concluidos': total_concluidos,
        'total_pendentes': total_pendentes,
    }
    
    return render(request, 'agendamentos/index.html', context)


@login_required
def novo_agendamento(request):
    if request.method == 'POST':
        form = AgendamentoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('index') # Volta para a lista após salvar
    else:
        form = AgendamentoForm()
    
    return render(request, 'agendamentos/form_agendamento.html', {'form': form})


@login_required
def editar_agendamento(request, pk):
    agendamento = get_object_or_404(Agendamento, pk=pk)
    if request.method == 'POST':
        form = AgendamentoForm(request.POST, instance=agendamento)
        if form.is_valid():
            form.save()
            return redirect('index')
    else:
        form = AgendamentoForm(instance=agendamento)
    return render(request, 'agendamentos/form_agendamento.html', {'form': form})


@login_required
def excluir_agendamento(request, pk):
    agendamento = get_object_or_404(Agendamento, pk=pk)
    if request.method == 'POST':
        agendamento.delete()
        return redirect('index')
    return render(request, 'agendamentos/confirmar_exclusao.html', {'agendamento': agendamento})


@login_required
def novo_paciente(request):
    if request.method == 'POST':
        form = PacienteForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('lista_pacientes') # Redireciona para a lista para ver o novo cadastro
    else:
        form = PacienteForm()
    # Usando o template padrão que criamos com o design moderno
    return render(request, 'agendamentos/cadastrar_paciente.html', {'form': form, 'editando': False})


@login_required
def concluir_agendamento(request, pk):
    agendamento = get_object_or_404(Agendamento, pk=pk)
    agendamento.status = 'concluido'
    agendamento.save()
    return redirect('index')


@login_required
def novo_dentista(request):
    if request.method == 'POST':
        form = DentistaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('index')
    else:
        form = DentistaForm()
    return render(request, 'agendamentos/form_dentista.html', {'form': form})


def registrar(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            # O ERRO ESTÁ AQUI: Use aspas no nome da rota!
            return redirect('index') 
    else:
        form = UserCreationForm()
    return render(request, 'registration/registrar.html', {'form': form})


@login_required
def perfil(request):
    if request.method == 'POST':
        # Verifica qual formulário foi enviado
        if 'btn_perfil' in request.POST:
            form_perfil = EditarPerfilForm(request.POST, instance=request.user)
            form_senha = PasswordChangeForm(request.user)
            if form_perfil.is_valid():
                form_perfil.save()
                messages.success(request, 'Dados atualizados com sucesso!')
                return redirect('perfil')
        
        elif 'btn_senha' in request.POST:
            form_senha = PasswordChangeForm(request.user, request.POST)
            form_perfil = EditarPerfilForm(instance=request.user)
            if form_senha.is_valid():
                user = form_senha.save()
                update_session_auth_hash(request, user)
                messages.success(request, 'Senha atualizada com sucesso!')
                return redirect('perfil')
    else:
        form_perfil = EditarPerfilForm(instance=request.user)
        form_senha = PasswordChangeForm(request.user)

    return render(request, 'registration/perfil.html', {
        'form_perfil': form_perfil,
        'form_senha': form_senha
    })