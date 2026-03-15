from django.contrib import admin
from .models import Dentista, Paciente, Agendamento

admin.site.register(Dentista)
admin.site.register(Paciente)
admin.site.register(Agendamento)