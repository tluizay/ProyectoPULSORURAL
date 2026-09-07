# PROYECTO PULSO RURAL
## 1.Proyecto - Qué problema resuleve
Es una aplicación, enfocada en conectar distintas fuentes de datos publicos y presentarlos en base a una zona dentro de la comunidad de castilla y león.
El objetivo de este proyecto es facilitar el acceso y la interpretación de datos público, los cuales se encuentra aislados uno de otros o bien con su propio
sistema de identificación nominal. Esta aplicación esta enfocada en el sector agrícola, debido al volumen de datos inutilizados en esta área.

Es una herramieta que transforma datos y en algunas áreas son interpretados por IA, para la sintesis de la información.

## 2.Herramientas - Qué utiliza
### Desarrollo Web y API

Django: Framework web de alto nivel para Python; maneja la estructura general de la aplicación, el enrutamiento, la administración y la base de datos.

asgiref: Interfaz de puerta de enlace de servidor asíncrono; necesaria para que Django gestione peticiones asíncronas (ASGI).

websockets: Biblioteca para construir servidores y clientes WebSocket, permitiendo comunicación bidireccional en tiempo real.

httpx / requests: Clientes HTTP para realizar peticiones a servicios o API externas (HTTPX soporta llamadas asíncronas).

### Análisis de Datos y Ciencia

pandas: Herramienta fundamental para la manipulación y análisis de datos estructurados mediante tablas (DataFrames).

numpy: Biblioteca base para cálculo numérico masivo y operaciones con matrices o arreglos multidimensionales.

xarray: Extensión de NumPy orientada a datos multidimensionales etiquetados (muy usada en datos meteorológicos, satelitales y climáticos).

### Geodatos, GIS y Mapas

rasterio: Manejo, lectura y escritura de imágenes satelitales y datos ráster geoespaciales.

geopy / geographiclib: Herramientas para geocodificación (convertir direcciones a coordenadas) y cálculo de distancias sobre la superficie terrestre.

geojson / xyzservices: Lectura/escritura del formato GeoJSON y proveedores de capas de mapas base en loseta (tiles).

affine: Realiza transformaciones matrices afines, clave para mapear coordenadas de píxeles a coordenadas geográficas.

Inteligencia Artificial y Modelos

pydantic: Validación de datos y gestión de configuraciones mediante tipos de Python; ampliamente usado para estructurar respuestas de IA y API.

Visualización y Tratamiento de Imágenes

matplotlib: Biblioteca principal para la creación de gráficos 2D y visualización estática de datos.

pillow (PIL): Procesamiento, manipulación y edición de imágenes (formatos JPG, PNG, etc.).

### Base de Datos y Seguridad

psycopg: Controlador (driver) oficial para conectar Python y Django con bases de datos PostgreSQL.

cryptography: Funciones criptográficas de bajo nivel para cifrado, firma de datos y manejo de claves.

google-auth: Gestión de autenticación e identidades para servicios de Google Cloud.

### Inteligencia artificial
google-genai: SDK oficial para interactuar con los modelos de lenguaje y generación de Google (como Gemini).

### Modelo de extracción e interpretación

```text
               +----------------------------------+
               |        Vista / Controller        |
               +----------------------------------+
                             |     ^
           1. Pide información |     | 6. Devuelve objeto final
               de una ubicación|     |    (Datos + Análisis IA)
                             v     |
               +----------------------------------+
               |            AGREGADOR             |
               |       (Orquestador / Facade)     |
               +----------------------------------+
                 /                              ^
 2. Pide datos  / 3. Devuelve      4. Envía    / 5. Devuelve
    de la zona /    JSON limpio       datos   /    resumen
              v   /  de clima        + prompt/     ejecutivo
     +-----------------+          +------------------+
     |  Aemet Service  |          |  Gemini Service  |
     |   (Extracción)  |          |  (Interpretación)|
     +-----------------+          +------------------+
```


## Fuentes de datos
**Aement:** Agencia estatal metereologica
```text
Esta fuente tiene el siguiente sistemas:
[PULSORURAL] ---> 1. GET (URL API + api_key) ---> [AEMET OpenData]
[PULSORURAL] <--- 2. JSON { "datos": "https://..." } <--- [AEMET OpenData]
[PULSORURAL] ---> 3. GET (URL temporal) ---------> [Servidor de Datos AEMET]
[PULSORURAL] <--- 4. JSON con los datos crudos <--- [Servidor de Datos AEMET]
```


el punto de origen o la petición es un click en el mapa, por tanto el sistemas debe proveé una solucion a la
ubicación de donde solicita los datos. Cuenta con una estrategia fallback de cinco intentos donde busca cinco estaciones
más cercanas la punto reduciendo las posibilidades de retornar datos nulos.

La web esta diseñada para cargar datos al vuelo por tanto el inventario completo de estaciones se almacena en memoria/Redis (cache.set) durante 24 horas (CACHE_TTL_INVENTARIO_SEGUNDOS) para evitar descargar la lista de estaciones en cada llamada asimismo el método normalize() toma los datos devueltos por AEMET (datos_brutos) y corrige las inconsistencias del formato de origen mediante.

**sigpac:**