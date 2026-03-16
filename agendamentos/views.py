from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Agendamento, Procedimento
from .forms import AgendamentoForm, PacienteForm, DentistaForm, EditarPerfilForm, Paciente
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from .models import Agendamento, Dentista
from datetime import datetime
from django.contrib.auth import login, authenticate 
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from django.db.models import Count
from django.db.models.functions import ExtractMonth
from django.utils import timezone
from django.db.models import Count, Q
from django.db.models.functions import ExtractMonth
from .forms import ProcedimentoForm 
from datetime import timedelta
from reportlab.lib import colors
from .models import Agendamento


def exportar_pdf(request):
    periodo = request.GET.get('periodo', 'dia')
    hoje = timezone.now()
    
    if periodo == 'mes':
        agendamentos = Agendamento.objects.filter(data__month=hoje.month, data__year=hoje.year)
        titulo_relatorio = f"Relatório Mensal - {hoje.strftime('%m/%Y')}"
    elif periodo == 'ano':
        agendamentos = Agendamento.objects.filter(data__year=hoje.year)
        titulo_relatorio = f"Relatório Anual - {hoje.year}"
    else:
        agendamentos = Agendamento.objects.filter(data=hoje.date())
        titulo_relatorio = f"Relatório Diário - {hoje.strftime('%d/%m/%Y')}"

    context = {
        'agendamentos': agendamentos,
        'titulo': titulo_relatorio,
        'data_geracao': hoje,
        'total_procedimentos': agendamentos.count(),
    }

    html_string = render_to_string('agendamentos/pdf_relatorio.html', context)
    
    html = HTML(string=html_string, base_url=request.build_absolute_uri())
    pdf = html.write_pdf()

    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="relatorio_{periodo}.pdf"'
    return response


def editar_dentista(request, pk):
    dentista = get_object_or_404(Dentista, pk=pk)
    
    if request.method == 'POST':
        form = DentistaForm(request.POST, instance=dentista)
        if form.is_valid():
            form.save()
            messages.success(request, f"Os dados do Dr(a). {dentista.nome} foram atualizados!")
            return redirect('lista_dentistas')
    else:
        form = DentistaForm(instance=dentista)
    
    return render(request, 'agendamentos/form_dentista.html', {
        'form': form, 
        'titulo': 'Editar Dentista',
        'dentista': dentista
    })

def excluir_dentista(request, pk):
    dentista = get_object_or_404(Dentista, pk=pk)
    
    if request.method == 'POST':
        nome_dentista = dentista.nome
        dentista.delete()
        messages.warning(request, f"O Dr(a). {nome_dentista} foi removido do sistema.")
        return redirect('lista_dentistas')
    
    return render(request, 'agendamentos/confirmar_exclusao_dentista.html', {
        'dentista': dentista
    })


def lista_dentistas(request):
    dentistas = Dentista.objects.all() 
    return render(request, 'agendamentos/lista_dentistas.html', {'dentistas': dentistas})


@login_required
def imprimir_ficha_consulta(request, consulta_id):
    consulta = get_object_or_404(Agendamento, pk=consulta_id)
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'filename="Ficha_{consulta.paciente.nome}.pdf"'
    
    p = canvas.Canvas(response, pagesize=A4)
    largura, altura = A4

    p.setFillColor(colors.HexColor("#98b3db")) 
    p.rect(0, altura - 80, largura, 80, fill=1, stroke=0)
    
    p.setFillColor(colors.black)
    p.setFont("Helvetica-Bold", 18)
    p.drawString(40, altura - 45, "FICHA DE ATENDIMENTO CLÍNICO")
    
    p.setFont("Helvetica", 10)
    p.drawString(40, altura - 65, f"Gerado em: {timezone.now().strftime('%d/%m/%Y %H:%M')}")

    y = altura - 130
    p.setFillColor(colors.HexColor("#f8f9fa"))
    p.roundRect(30, y - 70, largura - 60, 85, 10, fill=1, stroke=1) 
    
    p.setFillColor(colors.black)
    p.setFont("Helvetica-Bold", 12)
    p.drawString(45, y + 2, "DADOS DO PACIENTE")
    
    p.setFont("Helvetica", 11)
    p.drawString(45, y - 20, f"Paciente: {consulta.paciente.nome}")
    p.drawString(45, y - 38, f"Idade: {consulta.paciente.idade} anos")
    p.drawString(45, y - 56, f"WhatsApp: {consulta.paciente.telefone if hasattr(consulta.paciente, 'telefone') else '---'}")

    y = y - 120
    p.setFillColor(colors.HexColor("#f8f9fa"))
    p.roundRect(30, y - 70, largura - 60, 85, 10, fill=1, stroke=1)
    
    p.setFillColor(colors.black)
    p.setFont("Helvetica-Bold", 12)
    p.drawString(45, y + 2, "DETALHES DO AGENDAMENTO")
    
    p.setFont("Helvetica", 11)
    p.drawString(45, y - 20, f"Data e Hora: {consulta.data_hora.strftime('%d/%m/%Y às %H:%M')}")
    p.drawString(45, y - 38, f"Dentista Responsável: Dr(a). {consulta.dentista.nome}")
    p.drawString(45, y - 56, f"Procedimento: {consulta.procedimento.nome if consulta.procedimento else 'Consulta Geral'}")

    y = y - 110
    p.setFont("Helvetica-Bold", 12)
    p.drawString(40, y, "EVOLUÇÃO E OBSERVAÇÕES DO DENTISTA")
    
    p.setStrokeColor(colors.lightgrey)
    line_y = y - 30
    for _ in range(12):
        p.line(40, line_y, largura - 40, line_y)
        line_y -= 25

    p.setFont("Helvetica-Oblique", 8)
    p.setFillColor(colors.grey)
    p.drawCentredString(largura/2, 30, "Este documento é para uso interno do consultório e contém dados confidenciais.")

    p.showPage()
    p.save()
    return response


def procedimento_excluir(request, pk):
    procedimento = get_object_or_404(Procedimento, pk=pk)
    if request.method == "POST":
        procedimento.delete()
        return redirect('procedimentos_lista')
    return render(request, 'agendamentos/confirmar_exclusao.html', {'objeto': procedimento})


def procedimento_novo(request):
    if request.method == "POST":
        form = ProcedimentoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('procedimentos_lista')
    else:
        form = ProcedimentoForm()
    
    return render(request, 'agendamentos/form_procedimento.html', {'form': form})

def procedimento_editar(request, pk):
    procedimento = get_object_or_404(Procedimento, pk=pk)
    
    if request.method == "POST":
        form = ProcedimentoForm(request.POST, instance=procedimento)
        if form.is_valid():
            form.save()
            return redirect('procedimentos_lista')
    else:
        form = ProcedimentoForm(instance=procedimento)
    
    return render(request, 'agendamentos/form_procedimento.html', {'form': form})


def procedimentos_lista(request):
    procedimentos = Procedimento.objects.all().order_by('nome')
    return render(request, 'agendamentos/procedimentos.html', {'procedimentos': procedimentos})


@login_required
def dashboard(request):
    hoje = timezone.now().date()
    
    ano_selecionado = request.GET.get('ano')
    if not ano_selecionado:
        ano_selecionado = hoje.year
    else:
        ano_selecionado = int(ano_selecionado)

    anos_disponiveis = Agendamento.objects.dates('data_hora', 'year', order='DESC')
    anos = [data.year for data in anos_disponiveis]
    
    if hoje.year not in anos:
        anos.append(hoje.year)

    consultas_hoje = Agendamento.objects.filter(data_hora__date=hoje).order_by('data_hora')

    relatorio_mensal = Agendamento.objects.filter(data_hora__year=ano_selecionado) \
        .annotate(mes=ExtractMonth('data_hora')) \
        .values('mes') \
        .annotate(
            total=Count('id'),
            concluidos=Count('id', filter=Q(status='concluido')),
            cancelados=Count('id', filter=Q(status='cancelado'))
        ).order_by('mes')

    nomes_meses = {
        1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril', 5: 'Maio', 6: 'Junho',
        7: 'Julho', 8: 'Agosto', 9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'
    }

    for item in relatorio_mensal:
        item['nome_mes'] = nomes_meses.get(item['mes'])

    total_ano = Agendamento.objects.filter(data_hora__year=ano_selecionado).count()
    pacientes_novos = Paciente.objects.count()

    context = {
        'consultas_hoje': consultas_hoje,
        'relatorio_mensal': relatorio_mensal,
        'total_ano': total_ano,
        'pacientes_novos': pacientes_novos,
        'hoje': hoje,
        'ano_selecionado': ano_selecionado,
        'anos': sorted(anos, reverse=True), 
    }
    return render(request, 'agendamentos/dashboard.html', context)


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
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="agenda_consultorio.pdf"'

    p = canvas.Canvas(response, pagesize=A4)
    largura, altura = A4

    p.setFont("Helvetica-Bold", 16)
    p.drawString(100, altura - 50, "🦷 Relatório de Agendamentos - Consultório")
    p.setFont("Helvetica", 10)
    p.drawString(100, altura - 70, f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    
    p.line(100, altura - 80, 500, altura - 80)

    y = altura - 110
    p.setFont("Helvetica-Bold", 11)
    p.drawString(100, y, "Data/Hora")
    p.drawString(220, y, "Paciente")
    p.drawString(380, y, "Dentista")
    p.drawString(480, y, "Status")

    y -= 20
    p.setFont("Helvetica", 10)
    consultas = Agendamento.objects.all().order_by('data_hora')

    for c in consultas:
        if y < 50:
            p.showPage()
            y = altura - 50
        
        p.drawString(100, y, c.data_hora.strftime('%d/%m/%Y %H:%M'))
        p.drawString(220, y, c.paciente.nome[:25]) # Limita nome longo
        p.drawString(380, y, c.dentista.nome[:15])
        p.drawString(480, y, c.status.capitalize())
        y -= 20

    p.showPage()
    p.save()
    return response


@login_required
def index(request):
    busca = request.GET.get('search')
    filtro_data = request.GET.get('data')
    hoje = timezone.now().date()
    
    consultas = Agendamento.objects.all().order_by('data_hora')

    if busca:
        consultas = consultas.filter(paciente__nome__icontains=busca)
    
    if filtro_data == 'hoje':
        consultas = consultas.filter(data_hora__date=hoje)
    elif filtro_data == 'amanha':
        amanha = hoje + timedelta(days=1)
        consultas = consultas.filter(data_hora__date=amanha)

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
            agendamento = form.save(commit=False)
            
            if agendamento.procedimento and not agendamento.valor_final:
                agendamento.valor_final = agendamento.procedimento.valor
            
            agendamento.save()
            return redirect('index')
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
            return redirect('lista_pacientes')
    else:
        form = PacienteForm()
    
    return render(request, 'agendamentos/form_paciente.html', {'form': form, 'editando': False})
    return render(request, 'agendamentos/form_paciente.html', {'form': form, 'editando': False})


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
            return redirect('index') 
    else:
        form = UserCreationForm()
    return render(request, 'registration/registrar.html', {'form': form})


@login_required
def perfil(request):
    if request.method == 'POST':
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