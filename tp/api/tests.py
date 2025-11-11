from django.test import TestCase
from .services import RevisionService
from .models import Revision


class RevisionServiceTest(TestCase):
    def setUp(self):
        self.service = RevisionService()

    def test_vehiculo_seguro(self):
        """
        Caso “Vehículo seguro”: Se probará que una combinación de puntajes que
        sume 80 califique correctamente al vehículo como "seguro".
        """
        resultados = [{'puntuacion': 10} for _ in range(8)]  # Total: 80

        estado = self.service.calcular_estado_final(resultados)
        self.assertEqual(estado, Revision.EstadoRevision.SEGURO)

    def test_rechequeo_por_puntaje_bajo(self):
        """
        Caso “Rechequeo por puntaje total bajo”: Se simulará una revisión con
        puntajes cuya suma sea menor a 40 y se verificará que el sistema determine
        la necesidad de un "rechequeo".
        """
        resultados = [{'puntuacion': 1} for _ in range(8)]  # Total: 8

        estado = self.service.calcular_estado_final(resultados)
        self.assertEqual(estado, Revision.EstadoRevision.RECHEQUEO)

    def test_rechequeo_por_punto_critico(self):
        """
        Se diseñará un caso donde el puntaje total sea superior a 40 (ej: 65),pero
        uno de los 8 puntos tenga una nota inferior a 5 (ej: 3). La prueba deberá
        confirmar que, a pesar del puntaje total, el resultado siga siendo "rechequeo".
        """
        resultados = [{'puntuacion': 10} for _ in range(8)]
        resultados[0]['puntuacion'] = 4  # Total: 74 pero con punto < 5

        estado = self.service.calcular_estado_final(resultados)
        self.assertEqual(estado, Revision.EstadoRevision.RECHEQUEO)

    def test_caso_intermedio(self):
        """
        Caso intermedio: Se verificará el comportamiento para un vehículo que aprueba
        pero no llega a ser calificado como "seguro" (puntaje entre 40 y 80).
        """
        resultados = [{'puntuacion': 7} for _ in range(8)]  # Total: 56

        estado = self.service.calcular_estado_final(resultados)
        self.assertEqual(estado, Revision.EstadoRevision.SEGURO)
