from typing import List, Dict
from .models import Revision


class RevisionService:
    """
    Contiene la lógica de negocio para procesar una revisión.
    Está aislado de Django (no sabe de vistas ni de requests).
    """

    def calcular_estado_final(self, resultados: List[Dict]) -> str:
        puntaje_total = sum(item['puntuacion'] for item in resultados)
        puntaje_minimo = min(item['puntuacion'] for item in resultados)

        if puntaje_total < 40 or puntaje_minimo < 5:
            return Revision.EstadoRevision.RECHEQUEO

        return Revision.EstadoRevision.SEGURO
