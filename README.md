# Trabajo Práctico Integrador - TAP

## Tabla de contenidos
- [Requerimientos funcionales](#requerimientos-funcionales)
- [Endpoints](#endpoints)
- [Autenticación](#autenticación)
- [Base de datos](#base-de-datos)
- [Testing](#testing)
- [Cómo ejecutar](#cómo-ejecutar)
- [Dependencias](#dependencias)
- [Diagrama de clases](#diagrama-de-clases)
- [Modelo de datos](#modelo-de-datos)

## Requerimientos funcionales
1. El usuario dueño del vehículo deberá solicitar turno para la revisión anual del estado de su vehículo. 

2. Para solicitar turno deberá ingresar su número de matrícula.

3. El sistema deberá mostrar la disponibilidad de turnos para la selección por parte del usuario.

4. Se deberá confirmar por parte del usuario. 

5. En el proceso de chequeo un usuario con el rol adecuado, completará el resultado obtenido en cada punto evaluado.

6. Se puntua de 1 a 10 para cada paso.

7. Una vez que se evaluan todos los puntos, si en total se obtienen 80 puntos se califica al vehículo como seguro. Si se obtienen menos de 40 puntos, deberá rechequear y el usuario deberá informar en una observación al dueño del vehículo donde están los problemas que reflejan la puntuación. Además si un vehiculo obtiene menos de 5 puntos en alguno de los chequeos también deberá ser rechequeado.

8. Se consideran 8 puntos a chequear.

## Endpoints
- `GET /api/turnos/disponibles/`: Lista todos los turnos disponibles.
- `POST /api/turnos/<id>/confirmar/`: Confirma un turno específico. Requiere parámetro `matricula`.
- `POST /api/revisiones/`: Crea una nueva revisión de vehículo. **Requiere autenticación.**
- `POST /api/login/`: Autentica a un usuario y devuelve un token de acceso.

## Autenticación
Ejemplo de solicitud para obtener un token de autenticación:
```bash
curl -X POST http://localhost:8000/api/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "admin"
  }'
```
Ejemplo de solicitud autenticada para crear una revisión:
```bash
curl -X POST http://localhost:8000/api/revisiones/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Token 9bdfed6840f80f646ad2be0ba1a090313659c2d2" \
  -d '{
    "turno_id": 1,
    "observacion": "Vehículo en buen estado general.",
    "resultados": [
      {"punto_chequeo_id": 1, "puntuacion": 8},
      {"punto_chequeo_id": 2, "puntuacion": 7},
      {"punto_chequeo_id": 3, "puntuacion": 9},
      {"punto_chequeo_id": 4, "puntuacion": 6},
      {"punto_chequeo_id": 5, "puntuacion": 8},
      {"punto_chequeo_id": 6, "puntuacion": 7},
      {"punto_chequeo_id": 7, "puntuacion": 9},
      {"punto_chequeo_id": 8, "puntuacion": 10}
    ]
  }'
```

## Base de datos
**PostgreSQL**: Aunque para el desarrollo inicial Django funciona bien con SQLite, se opta por PostgreSQL pensando en un entorno más realista y de producción. Es una base de datos relacional potente, de código abierto y muy fiable, ideal para asegurar la integridad de los datos entre vehículos, dueños, turnos y revisiones.

## Testing

### Pruebas Unitarias
- **Objetivo**: Probar la lógica de negocio en completo aislamiento, sin depender de la base de datos, la red u otros componentes externos.
- **Tecnología**: Django TestCase (`django.test.TestCase`).
- **Casos testeados**:
  1. **Caso "Vehículo seguro"**: Se probará que una combinación de puntajes que sume más de 80 califique correctamente al vehículo como "seguro".
  2. **Caso "Rechequeo por puntaje total bajo"**: Se simulará una revisión con puntajes cuya suma sea menor a 40 y se verificará que el sistema determine la necesidad de un "rechequeo".
  3. **Caso "Rechequeo por punto crítico"**: Se diseñará un caso donde el puntaje total sea superior a 40 (ej: 65), pero uno de los 8 puntos tenga una nota inferior a 5 (ej: 3). La prueba deberá confirmar que, a pesar del puntaje total, el resultado siga siendo "rechequeo".
  4. **Caso intermedio**: Se verificará el comportamiento para un vehículo que aprueba pero no llega a ser calificado como "seguro" (puntaje entre 40 y 80).

Ejecutar las pruebas unitarias:
```bash
docker compose exec web python manage.py test
```

### Pruebas de Integración
- **Objetivo**: Verificar que las distintas partes del sistema (API, lógica y base de datos) se comunican bien entre sí. Se simulan peticiones HTTP a los endpoints y se comprueba que la respuesta y el estado de la base de datos sean los correctos.
- **Tecnología**: Cliente de pruebas integrado en Django (`django.test.Client`). Permite simular peticiones GET, POST, etc., a la API sin necesidad de levantar un servidor real.
- **Módulos testeados**:
  1. **Endpoint de Disponibilidad de Turnos** (`GET /api/turnos/disponibles/`): Se crearán varios turnos en la base de datos de prueba, algunos ya ocupados y otros libres. La prueba hará una petición a este endpoint y verificará que la respuesta JSON contenga únicamente los turnos disponibles.
  2. **Endpoint de Confirmación de Turno** (`POST /api/turnos/<id>/confirmar/`): Se creará un turno disponible en la base de datos. La prueba simulará que un usuario (dueño de un vehículo) hace una petición POST para confirmar ese turno. Luego, se verificará en la base de datos que el estado del turno haya cambiado a "confirmado" y que se haya asociado correctamente con el vehículo del usuario.
  3. **Endpoint de Creación de Revisión** (`POST /api/revisiones/`): Este es un flujo clave. La prueba simulará que un usuario con rol de inspector envía los 8 puntajes de una revisión a través de la API. Se verificará que se cree un nuevo registro de `Revision` en la base de datos, junto con sus 8 puntos de chequeo asociados, y que la API devuelva un código de éxito (201 Created). También se probará qué pasa si se envían datos incorrectos (ej: solo 7 puntajes), esperando un error (400 Bad Request).


## Cómo ejecutar
### 1. Levantar los contenedores
```bash
docker compose up -d
```
Los servicios corren en contenedores independientes:
- Base de datos PostgreSQL en puerto `5432`.
- API RESTful Django en puerto `8000`.

### 2. Acceder a la aplicación
- API: http://localhost:8000/api
- Admin: http://localhost:8000/admin
  - Usuario: `admin`
  - Contraseña: `admin`

## Dependencias
- **Django**: Framework principal para desarrollar aplicaciones web en Python.
- **djangorestframework**: Extensión para Django que facilita la creación de APIs REST.
- **psycopg2-binary**: Driver que permite a Django conectarse y trabajar con bases de datos PostgreSQL.

## Diagrama de clases
<img src="docs/diagrama_clases.drawio.png" width="600"/>

## Modelo de datos
<img src="docs/modelo_datos.drawio.png" width="600"/>

## Consideraciones
- Simplificación de los modelos:
  - `Vehiculo` no contiene `marca`, `modelo` ni `año`.
  - `Usuario` no contiene `email`.
  - `PuntoChequeo` no contiene `descripcion`.