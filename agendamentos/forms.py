from django import forms
from .models import Agendamento, Paciente, Dentista, Procedimento 
from django.contrib.auth.models import User
from datetime import date

# --- FORMULÁRIO DE PROCEDIMENTOS (O que estava faltando!) ---
class ProcedimentoForm(forms.ModelForm):
    class Meta:
        model = Procedimento
        fields = ['nome', 'valor', 'descricao']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Limpeza'}),
            'valor': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

# --- FORMULÁRIO DE PACIENTES ---
class PacienteForm(forms.ModelForm):
    class Meta:
        model = Paciente
        fields = '__all__'
        widgets = {
            'cpf': forms.TextInput(attrs={'placeholder': '000.000.000-00', 'class': 'form-control'}),
            'telefone': forms.TextInput(attrs={'placeholder': '(00) 00000-0000', 'class': 'form-control'}),
            'data_nascimento': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }

    def clean_data_nascimento(self):
        data_nasc = self.cleaned_data.get('data_nascimento')
        if data_nasc and data_nasc > date.today():
            raise forms.ValidationError("Ops! O paciente ainda não nasceu? A data não pode ser no futuro.")
        return data_nasc

# --- FORMULÁRIO DE AGENDAMENTOS ---
class AgendamentoForm(forms.ModelForm):
    class Meta:
        model = Agendamento
        fields = ['paciente', 'dentista', 'data_hora', 'procedimento', 'status'] 
        widgets = {
            'data_hora': forms.DateTimeInput(
                attrs={'type': 'datetime-local', 'class': 'form-control'},
                format='%Y-%m-%dT%H:%M'
            ),
            'procedimento': forms.Select(attrs={'class': 'form-select'}),
            'paciente': forms.Select(attrs={'class': 'form-select'}),
            'dentista': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['data_hora'].input_formats = ['%Y-%m-%dT%H:%M']

    def clean(self):
        cleaned_data = super().clean()
        dentista = cleaned_data.get('dentista')
        data_hora = cleaned_data.get('data_hora')

        if dentista and data_hora:
            conflito = Agendamento.objects.filter(
                dentista=dentista, 
                data_hora=data_hora
            ).exclude(pk=self.instance.pk if self.instance.pk else None).exists()

            if conflito:
                raise forms.ValidationError(
                    f"O(a) Dr(a). {dentista.nome} já possui um agendamento para este horário."
                )
        return cleaned_data

# --- OUTROS FORMULÁRIOS ---
class DentistaForm(forms.ModelForm):
    class Meta:
        model = Dentista
        fields = ['nome', 'especialidade', 'cro', 'telefone', 'email']
        widgets = {f: forms.TextInput(attrs={'class': 'form-control'}) for f in fields}

class EditarPerfilForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']
        widgets = {f: forms.TextInput(attrs={'class': 'form-control'}) for f in fields}