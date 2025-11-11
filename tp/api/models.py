from django.db import models
from django.contrib.auth.models import User

# El usuario DUEÑO es anónimo, tomamos el admin de Django como INSPECTOR


class Vehiculo(models.Model):
    matricula = models.CharField(max_length=20, unique=True, primary_key=True)
    # Marca, modelo y año no son requeridos
    # No se relaciona con DUEÑO porque no existe

    def __str__(self):
        return self.matricula


class Turno(models.Model):
    class EstadoTurno(models.TextChoices):
        DISPONIBLE = 'DISPONIBLE', 'Disponible'
        CONFIRMADO = 'CONFIRMADO', 'Confirmado'
        COMPLETADO = 'COMPLETADO', 'Completado'
        CANCELADO = 'CANCELADO', 'Cancelado'

    fecha_hora = models.DateTimeField()
    estado = models.CharField(max_length=50, choices=EstadoTurno.choices, default=EstadoTurno.DISPONIBLE)
    vehiculo = models.ForeignKey(Vehiculo, on_delete=models.CASCADE, null=True, blank=True)
    # null=True: Le dice a la base de datos que puede almacenar un valor NULL en esta columna.
    # blank=True: Le dice a Django (en formularios como el del admin) que este campo puede dejarse en blanco.

    def __str__(self):
        return f"Turno el {self.fecha_hora.strftime('%d/%m/%Y a las %H:%M')} - {self.estado}"


class PuntoChequeo(models.Model):
    nombre = models.CharField(max_length=100)
    # Descripción no es requerida

    def __str__(self):
        return self.nombre


class Revision(models.Model):
    class EstadoRevision(models.TextChoices):
        SEGURO = 'SEGURO', 'Seguro'
        RECHEQUEO = 'RECHEQUEO', 'Rechequeo'

    turno = models.OneToOneField(Turno, on_delete=models.CASCADE)
    inspector = models.ForeignKey(User, on_delete=models.PROTECT)
    fecha_hora = models.DateTimeField(auto_now_add=True)
    observacion = models.TextField(blank=True, null=True)
    estado_final = models.CharField(max_length=50, choices=EstadoRevision.choices)

    def __str__(self):
        return f"Revisión para {self.turno.vehiculo.matricula} - {self.estado_final}"


class ResultadoPunto(models.Model):
    revision = models.ForeignKey(Revision, on_delete=models.CASCADE)
    punto = models.ForeignKey(PuntoChequeo, on_delete=models.PROTECT)
    puntuacion = models.IntegerField()  # De 1 a 10

    def __str__(self):
        return f"{self.punto.nombre}: {self.puntuacion}"
