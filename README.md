# Trabajo Práctico Integrador - TAP

## Tabla de contenidos
- [Requerimientos funcionales](#requerimientos-funcionales)
- [Arquitectura](#arquitectura)
- [Patrones de diseño](#patrones-de-diseño)
  - [Inyección de dependencias](#inyección-de-dependencias)
  - [MVC/MVT](#mvcmvt)
- [Principios de diseño](#principios-de-diseño)
  - [Separación de responsabilidades](#separación-de-responsabilidades)
  - [Inversión de dependencias](#inversión-de-dependencias)
- [Metodología de desarrollo](#metodología-de-desarrollo)
- [Base de datos](#base-de-datos)
  - [Diagrama de clases](#diagrama-de-clases)
  - [Modelo de datos](#modelo-de-datos)
  - [Consideraciones](#consideraciones)
- [Endpoints](#endpoints)
- [Autenticación](#autenticación)
- [Testing](#testing)
  - [Pruebas Unitarias](#pruebas-unitarias)
  - [Pruebas de Integración](#pruebas-de-integración)
- [Cómo ejecutar](#cómo-ejecutar)
- [Dependencias](#dependencias)
- [Demo](#demo)

## Requerimientos funcionales
1. El usuario dueño del vehículo deberá solicitar turno para la revisión anual del estado de su vehículo. 

2. Para solicitar turno deberá ingresar su número de matrícula.

3. El sistema deberá mostrar la disponibilidad de turnos para la selección por parte del usuario.

4. Se deberá confirmar por parte del usuario. 

5. En el proceso de chequeo un usuario con el rol adecuado, completará el resultado obtenido en cada punto evaluado.

6. Se puntua de 1 a 10 para cada paso.

7. Una vez que se evaluan todos los puntos, si en total se obtienen 80 puntos se califica al vehículo como seguro. Si se obtienen menos de 40 puntos, deberá rechequear y el usuario deberá informar en una observación al dueño del vehículo donde están los problemas que reflejan la puntuación. Además si un vehiculo obtiene menos de 5 puntos en alguno de los chequeos también deberá ser rechequeado.

8. Se consideran 8 puntos a chequear.

## Arquitectura
### Arquitectura de 3 Capas
1. **Capa de Presentación**: Es la interfaz con la que interactúa el usuario. En este caso, no hay una interfaz gráfica, pero los endpoints de la API son consumidos por un cliente. Este cliente puede ser una aplicación web (hecha con React, Angular, etc.), una app móvil, o herramientas de línea de comandos como curl. Su única responsabilidad es mostrar datos y capturar la entrada del usuario.

2. **Capa de Negocio**: Acá reside el "cerebro" de la aplicación. Esta capa procesa las entradas del usuario, aplica reglas de negocio y toma decisiones. La API de Django es esta capa. Recibe peticiones de la capa de presentación, procesa los datos (por ejemplo, calcula si un vehículo es seguro en `RevisionService`) y se comunica con la capa de datos.

3. **Capa de Datos**: Su única función es almacenar y gestionar los datos de la aplicación.

Si un mismo servidor combinara la lógica de negocio y la capa de datos, sería una arquitectura de 2 capas (cliente-servidor).

**Microservicios vs. Monolito**: Este proyecto sigue una arquitectura monolítica, en contraste, una arquitectura de microservicios dividiría la aplicación en servicios independientes (por ejemplo, un servicio para gestión de turnos, otro para revisiones, etc.), lo que puede ser beneficioso para aplicaciones muy grandes y complejas.

## Patrones de diseño
Soluciones ya probadas para problemas comunes.

### Inyección de dependencias
Se desacopla la lógica de negocio en la clase `RevisionService` y se inyecta como dependencia en el constructor de la vista `CrearChequeoView` (el controlador). Esto permite cambiar la lógica de negocio (por ejemplo, modificar los umbrales de puntaje) sin tocar el código del controlador, manteniendo así la separación de responsabilidades.

### MVC/MVT
Django usa el patrón Model View Template (MVT):

- **Model**: Define la estructura de datos (`Vehiculo`, `Turno`, `Revision`, `ResultadoChequeo`).
- **View**: Procesa peticiones HTTP y coordina la lógica de negocio.
- **Template**: Como es una API REST, usamos **serializers** para transformar datos entre JSON y modelos Django.

## Principios de diseño
### Separación de responsabilidades
Cada módulo tiene una única responsabilidad:
- **Views**: Peticiones HTTP
- **Services**: Lógica de negocio
- **Models**: Estructura de datos
- **Serializers**: Transformación JSON a Modelos

### Inversión de dependencias
La vista `CrearChequeoView` (alto nivel) inyecta `RevisionService` como dependencia, delegando la lógica de negocio al servicio (bajo nivel). Esto permite cambiar la lógica de cálculo sin tocar el controlador.

## Metodología de desarrollo
**Cascada**: Proceso secuencial y lineal:
1. Requisitos
2. Diseño
3. Implementación
4. Pruebas
5. Despliegue
6. Mantenimiento

## Base de datos
**¿Por qué una base relacional?**: La estructura de datos es rígida, bien definida, y existen relaciones fuertes entre sus entidades. Además, la integridad de los datos es crítica, ya que varios usuarios pueden estar interactuando con los mismos turnos simultáneamente. Por esta razón, necesitamos utilizar transacciones para evitar que dos usuarios confirmen el mismo turno.

**PostgreSQL**: Aunque para el desarrollo inicial Django funciona bien con SQLite, se opta por PostgreSQL pensando en un entorno más realista y de producción. Es una base de datos relacional potente, de código abierto y muy fiable, ideal para asegurar la integridad de los datos entre vehículos, dueños, turnos y revisiones.

### Diagrama de clases
<img src="docs/diagrama_clases.drawio.png" width="600"/>

### Modelo de datos
<img src="docs/modelo_datos.drawio.png" width="600"/>

### Consideraciones
Simplificación de los modelos:
- `Vehiculo` no contiene `marca`, `modelo` ni `año`.
- `Usuario` no contiene `email`.
- `PuntoChequeo` no contiene `descripcion`.

## Endpoints
- `GET /api/turnos/disponibles/`: Lista todos los turnos disponibles.
- `POST /api/turnos/<id>/confirmar/`: Confirma un turno específico. Requiere parámetro `matricula`.
- `POST /api/revisiones/`: Crea una nueva revisión de vehículo. **Requiere autenticación.**
- `POST /api/login/`: Autentica a un usuario y devuelve un token de acceso.
- `GET /api/vehiculos/<patente>/`: Devuelve el estado del vehículo (SEGURO o RECHEQUEO) según su última revisión.

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

## Testing

### Pruebas Unitarias
- **Objetivo**: Probar la lógica de negocio en completo aislamiento, sin depender de la base de datos, la red u otros componentes externos.
- **Tecnología**: Django TestCase (`django.test.TestCase`).
- **Casos testeados**:
  1. **Caso "Vehículo seguro"**: Se probará que una combinación de puntajes que sume más de 80 califique correctamente al vehículo como "seguro".
  2. **Caso "Rechequeo por puntaje total bajo"**: Se simulará una revisión con puntajes cuya suma sea menor a 40 y se verificará que el sistema determine la necesidad de un "rechequeo".
  3. **Caso "Rechequeo por punto crítico"**: Se diseñará un caso donde el puntaje total sea superior a 40 (ej: 65), pero uno de los 8 puntos tenga una nota inferior a 5 (ej: 3). La prueba deberá confirmar que, a pesar del puntaje total, el resultado siga siendo "rechequeo".
  4. **Caso intermedio**: Se verificará el comportamiento para un vehículo que aprueba pero no llega a ser calificado como "seguro" (puntaje entre 40 y 80).

Comando para ejecutar las pruebas unitarias:
```bash
docker exec -it tp_tap-api-1 python manage.py test
```

Resultados de las pruebas unitarias:
```bash
Found 4 test(s).
Creating test database for alias 'default'...
System check identified no issues (0 silenced).
....
----------------------------------------------------------------------
Ran 4 tests in 0.003s

OK
Destroying test database for alias 'default'...
```
Los 4 casos funcionan correctamente ✅

### Pruebas de Integración
- **Objetivo**: Verificar que las distintas partes del sistema (API, lógica y base de datos) se comunican bien entre sí. Se simulan peticiones HTTP a los endpoints y se comprueba que la respuesta y el estado de la base de datos sean los correctos.
- **Tecnología**: Cliente de pruebas integrado en Django (`django.test.Client`). Permite simular peticiones GET, POST, etc., a la API sin necesidad de levantar un servidor real.
- **Módulos testeados**:
  1. **Endpoint de Disponibilidad de Turnos** (`GET /api/turnos/disponibles/`): Se crearán varios turnos en la base de datos de prueba, algunos ya ocupados y otros libres. La prueba hará una petición a este endpoint y verificará que la respuesta JSON contenga únicamente los turnos disponibles.
  2. **Endpoint de Confirmación de Turno** (`POST /api/turnos/<id>/confirmar/`): Se creará un turno disponible en la base de datos. La prueba simulará que un usuario (dueño de un vehículo) hace una petición POST para confirmar ese turno. Luego, se verificará en la base de datos que el estado del turno haya cambiado a "confirmado" y que se haya asociado correctamente con el vehículo del usuario.
  3. **Endpoint de Creación de Revisión** (`POST /api/revisiones/`): Este es un flujo clave. La prueba simulará que un usuario con rol de inspector envía los 8 puntajes de una revisión a través de la API. Se verificará que se cree un nuevo registro de `Revision` en la base de datos, junto con sus 8 puntos de chequeo asociados, y que la API devuelva un código de éxito (201 Created). También se probará qué pasa si se envían datos incorrectos (ej: solo 7 puntajes), esperando un error (400 Bad Request).

## Cómo ejecutar
### Prerequisitos
Docker
### 1. Levantar los contenedores
```bash
docker compose up -d
```
Tanto la base de datos como la API corren en contenedores separados:
- Base de datos en puerto `5432`.
- API RESTful en puerto `8000`.

### 2. Acceder a la API
- API: http://localhost:8000/api
- Admin: http://localhost:8000/admin
  - Usuario: `admin`
  - Contraseña: `admin`

## Dependencias
Declaradas en el `requirements.txt`:
- **Django**: Framework principal para desarrollar aplicaciones web en Python.
- **djangorestframework**: Extensión para Django que facilita la creación de APIs REST.
- **psycopg2-binary**: Driver que permite a Django conectarse y trabajar con bases de datos PostgreSQL.

## Demo
Recorrido de los casos:
1. Levantar local
2. Tomar un turno (anónimo):
  - MVP: desde patente
  - Usuario técnico (autenticado):
    - MVP: No es necesario registro
	- Servicios privados (requieren auth)
3. Hacer la revisión
4. Establecer un puntaje
5. Publicar y generar el resultado
6. Visualizar condiciones de su vehículo (usuario dueño)

### Comandos
1. Levantar local
```bash
docker compose up -d
docker ps
```
2. Tomar un turno (anónimo):
  - MVP: desde patente
  - Usuario técnico (autenticado):
    - MVP: No es necesario registro
	- Servicios privados (requieren auth)
```bash
curl -X GET http://localhost:8000/api/turnos/disponibles/
```
Suponiendo que el usuario quiere tomar el turno con id=1:
```bash
curl -X POST http://localhost:8000/api/turnos/1/confirmar/ \
  -H "Content-Type: application/json" \
  -d '{
    "matricula": "ABC123"
  }'
```
3. Hacer la revisión
4. Establecer un puntaje
5. Publicar y generar el resultado
```bash
curl -X POST http://localhost:8000/api/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "admin"
  }'
```
Suponiendo que el token obtenido es `aa677632f527861623478bc65fc66524041008d3`
```bash
curl -X POST http://localhost:8000/api/revisiones/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Token aa677632f527861623478bc65fc66524041008d3" \
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
6. Visualizar condiciones de su vehículo (usuario dueño)
Suponiendo que la patente es `ABC123`:
```bash
curl -X GET http://localhost:8000/api/vehicles/ABC123/
```