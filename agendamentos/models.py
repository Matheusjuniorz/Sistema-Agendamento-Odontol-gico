from django.db import models
from datetime import date


class Dentista(models.Model):
    nome = models.CharField(max_length=100)
    cro = models.CharField(max_length=20, unique=True, verbose_name="Registro CRO")
    especialidade = models.CharField(max_length=100)
    telefone = models.CharField(max_length=15)
    email = models.EmailField(blank=True, null=True)

    def __str__(self):
        return f"Dr(a). {self.nome} - {self.especialidade}"


class Paciente(models.Model):
    nome = models.CharField(max_length=100)
    cpf = models.CharField(max_length=14, unique=True)
    email = models.EmailField()
    telefone = models.CharField(max_length=15)
    data_nascimento = models.DateField()

    def __str__(self):
        return self.nome

    @property
    def idade(self):
        hoje = date.today()
        return hoje.year - self.data_nascimento.year - (
            (hoje.month, hoje.day) < (self.data_nascimento.month, self.data_nascimento.day)
        )



class Agendamento(models.Model):
    STATUS_CHOICES = [
        ('agendado', 'Agendado'),
        ('cancelado', 'Cancelado'),
        ('concluido', 'Concluído'),
    ]

    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE) 
    dentista = models.ForeignKey(Dentista, on_delete=models.CASCADE)
    data_hora = models.DateTimeField()
    
    procedimento = models.ForeignKey('Procedimento', on_delete=models.SET_NULL, null=True, blank=True)
    
    valor_final = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='agendado')

    def __str__(self):
        return f"{self.paciente} - {self.data_hora.strftime('%d/%m/%Y %H:%M')}"


class Procedimento(models.Model):
    nome = models.CharField(max_length=100, verbose_name="Nome do Procedimento")
    descricao = models.TextField(blank=True, null=True, verbose_name="Descrição")
    valor = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Valor (R$)")

    def __clstr__(self):
        return self.nome