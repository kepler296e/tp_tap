from rest_framework import generics, status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db import transaction
from .models import Turno, Revision, PuntoChequeo, ResultadoPunto, Vehiculo
from .serializers import *
from .services import RevisionService

# --- Endpoints Públicos (para el Dueño del Vehículo) ---


class TurnosDisponiblesView(generics.ListAPIView):
    """
    Devuelve una lista de todos los turnos con estado 'DISPONIBLE'.
    """
    queryset = Turno.objects.filter(estado=Turno.EstadoTurno.DISPONIBLE).order_by('fecha_hora')
    serializer_class = TurnoDisponibleSerializer
    permission_classes = [permissions.AllowAny]  # Cualquiera puede ver los turnos


class VehiculosListView(generics.ListAPIView):
    """
    Devuelve una lista de todos los vehículos registrados.
    """
    queryset = Vehiculo.objects.all().order_by('matricula')
    serializer_class = VehiculoSerializer
    permission_classes = [permissions.AllowAny]


class ConfirmarTurnoView(APIView):
    """
    Permite a un usuario confirmar un turno disponible para su vehículo.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request, pk, *args, **kwargs):
        # 1. Validar que nos pasen una matrícula
        serializer = TurnoConfirmarSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        matricula = serializer.validated_data['matricula']

        # 2. Buscar el turno y asegurarse de que esté disponible
        try:
            turno = Turno.objects.get(pk=pk, estado=Turno.EstadoTurno.DISPONIBLE)
        except Turno.DoesNotExist:
            return Response({'error': 'El turno no existe o ya no está disponible.'}, status=status.HTTP_404_NOT_FOUND)

        # 3. Obtener o crear el vehículo
        vehiculo, created = Vehiculo.objects.get_or_create(matricula=matricula)

        # 4. Asociar el vehículo al turno y cambiar su estado
        turno.vehiculo = vehiculo
        turno.estado = Turno.EstadoTurno.CONFIRMADO
        turno.save()

        return Response({'status': 'Turno confirmado exitosamente.'}, status=status.HTTP_200_OK)


# --- Endpoints Privados (para el Inspector) ---

class CrearChequeoView(APIView):
    """
    Permite a un inspector autenticado cargar los resultados de una revisión.
    """
    permission_classes = [permissions.IsAuthenticated]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.revision_service = RevisionService()

    def post(self, request, *args, **kwargs):
        serializer = ChequeoCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        validated_data = serializer.validated_data
        turno_id = validated_data['turno_id']
        resultados_data = validated_data['resultados']

        try:
            turno = Turno.objects.get(pk=turno_id, estado=Turno.EstadoTurno.CONFIRMADO)
        except Turno.DoesNotExist:
            return Response({'error': 'El turno no existe o no está confirmado.'}, status=status.HTTP_404_NOT_FOUND)

        estado_final = self.revision_service.calcular_estado_final(resultados_data)

        try:
            with transaction.atomic():
                revision = Revision.objects.create(
                    turno=turno,
                    inspector=request.user,
                    estado_final=estado_final,
                    observacion=validated_data.get('observacion', '')
                )

                resultados_a_crear = []
                for res_data in resultados_data:
                    punto = PuntoChequeo.objects.get(pk=res_data['punto_chequeo_id'])
                    resultados_a_crear.append(
                        ResultadoPunto(
                            revision=revision,
                            punto=punto,
                            puntuacion=res_data['puntuacion']
                        )
                    )
                ResultadoPunto.objects.bulk_create(resultados_a_crear)

                turno.estado = Turno.EstadoTurno.COMPLETADO
                turno.save()

        except PuntoChequeo.DoesNotExist:
            return Response({'error': 'Uno de los puntos de chequeo no existe.'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': 'Ocurrió un error inesperado al guardar la revisión.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({
            'status': 'Revisión creada exitosamente',
            'revision_id': revision.id,
            'estado_final': estado_final
        }, status=status.HTTP_201_CREATED)
