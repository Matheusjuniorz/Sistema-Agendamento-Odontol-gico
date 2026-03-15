from django import forms
from .models import Agendamento, Paciente, Dentista
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import date


class AgendamentoForm(forms.ModelForm):
    class Meta:
        model = Agendamento
        fields = ['paciente', 'dentista', 'data_hora', 'status']
        widgets = {
            'data_hora': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        dentista = cleaned_data.get('dentista')
        data_hora = cleaned_data.get('data_hora')

        if dentista and data_hora:
            # Verifica se já existe um agendamento para este dentista neste horário
            # Excluindo o próprio agendamento (caso seja uma edição)
            conflito = Agendamento.objects.filter(
                dentista=dentista, 
                data_hora=data_hora
            ).exclude(pk=self.instance.pk if self.instance else None).exists()

            if conflito:
                raise forms.ValidationError(
                    f"O(a) Dr(a). {dentista.nome} já possui um agendamento para este horário ({data_hora.strftime('%d/%m/%Y %H:%M')})."
                )
        
        return cleaned_data
    
    
class EditarPerfilForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']


class AgendamentoForm(forms.ModelForm):
    class Meta:
        model = Agendamento
        fields = ['paciente', 'dentista', 'data_hora', 'procedimento']
        widgets = {
            # Isso aqui faz o campo de data virar um seletor de calendário e hora real
            'data_hora': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'procedimento': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }


class PacienteForm(forms.ModelForm):
    class Meta:
        model = Paciente
        fields = '__all__'
        widgets = {
            'cpf': forms.TextInput(attrs={
                'placeholder': '000.000.000-00',
                'class': 'form-control'
            }),
            'telefone': forms.TextInput(attrs={
                'placeholder': '(00) 00000-0000',
                'class': 'form-control'
            }),
            'data_nascimento': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
        }

    def clean_data_nascimento(self):
        data_nasc = self.cleaned_data.get('data_nascimento')
        # Verificamos se a data existe e se é maior que hoje
        if data_nasc and data_nasc > date.today():
            raise forms.ValidationError("Ops! O paciente ainda não nasceu? A data não pode ser no futuro.")
        return data_nasc


class AgendamentoForm(forms.ModelForm):
    class Meta:
        model = Agendamento
        fields = ['paciente', 'dentista', 'data_hora', 'procedimento']
        widgets = {
            'data_hora': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'procedimento': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        dentista = cleaned_data.get('dentista')
        data_hora = cleaned_data.get('data_hora')

        if dentista and data_hora:
            # Verifica se já existe um agendamento para o MESMO dentista na MESMA hora
            # Excluindo o próprio agendamento atual (importante para quando estiver editando)
            conflito = Agendamento.objects.filter(
                dentista=dentista, 
                data_hora=data_hora
            ).exclude(pk=self.instance.pk)

            if conflito.exists():
                raise forms.ValidationError(
                    f"Ops! O Dr(a). {dentista.nome} já possui um agendamento para este horário."
                )

        return cleaned_data
    

class DentistaForm(forms.ModelForm):
    class Meta:
        model = Dentista
        fields = ['nome', 'especialidade', 'cro', 'telefone', 'email']