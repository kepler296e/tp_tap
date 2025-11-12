from rest_framework import serializers
from .models import Turno, Revision, ResultadoPunto, PuntoChequeo, Vehiculo

# --- Serializadores para el flujo del DUEÑO (Públicos) ---


class VehiculoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehiculo
        fields = ['matricula']


class TurnoDisponibleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Turno
        fields = ['id', 'fecha_hora']


class TurnoConfirmarSerializer(serializers.Serializer):
    matricula = serializers.CharField(max_length=20)


class EstadoVehiculoSerializer(serializers.Serializer):
    matricula = serializers.CharField()
    estado = serializers.CharField()


# --- Serializadores para el flujo del INSPECTOR (Privados) ---

class ResultadoPuntoCreateSerializer(serializers.ModelSerializer):
    punto_chequeo_id = serializers.IntegerField()

    class Meta:
        model = ResultadoPunto
        fields = ['punto_chequeo_id', 'puntuacion']


class ChequeoCreateSerializer(serializers.Serializer):
    turno_id = serializers.IntegerField()
    observacion = serializers.CharField(required=False, allow_blank=True)
    resultados = ResultadoPuntoCreateSerializer(many=True)

    def validate_resultados(self, value):
        if len(value) != 8:
            raise serializers.ValidationError("Se deben proporcionar exactamente 8 resultados.")
        return value
