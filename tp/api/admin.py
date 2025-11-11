from django.contrib import admin
from .models import Turno, Vehiculo, PuntoChequeo, Revision, ResultadoPunto

admin.site.register(Turno)
admin.site.register(Vehiculo)
admin.site.register(PuntoChequeo)
admin.site.register(Revision)
admin.site.register(ResultadoPunto)
