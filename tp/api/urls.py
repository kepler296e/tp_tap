from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token
from .views import *

urlpatterns = [
    # --- URLs Públicas ---
    # GET /api/turnos/disponibles/ -> Devuelve la lista de turnos DISPONIBLES
    path('turnos/disponibles/', TurnosDisponiblesView.as_view()),

    # POST /api/turnos/<id>/confirmar/ -> Confirma un turno
    path('turnos/<int:pk>/confirmar/', ConfirmarTurnoView.as_view()),

    # GET /api/vehiculos/ -> Devuelve la lista de vehículos registrados
    path('vehiculos/', VehiculosListView.as_view()),

    # GET /api/vehicles/<patente>/ -> Devuelve el estado del vehículo
    path('vehicles/<str:patente>/', EstadoVehiculoView.as_view()),

    # --- URLs de Autenticación ---
    # POST /api/login/ -> Autentica un inspector y devuelve un token
    path('login/', obtain_auth_token, name='api-login'),

    # --- URLs Privadas ---
    # POST /api/revisiones/ -> Crea una nueva revisión (requiere autenticación)
    path('revisiones/', CrearChequeoView.as_view(), name='crear-revision'),
]
