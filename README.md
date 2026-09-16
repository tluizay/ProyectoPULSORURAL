# PROYECTO PULSO RURAL

## 1. Proyecto — Qué problema resuelve

Es una aplicación enfocada en conectar distintas fuentes de datos públicos y presentarlos en base a una zona dentro de la comunidad de Castilla y León.
El objetivo de este proyecto es facilitar el acceso y la interpretación de datos públicos, los cuales se encuentran aislados unos de otros o bien con su propio sistema de identificación nominal. Esta aplicación está enfocada en el sector agrícola, debido al volumen de datos inutilizados en esta área.

Es una herramienta que transforma datos y en algunas áreas son interpretados por IA, para la síntesis de la información.

**Funcionalidades principales**

- Mapa interactivo (Leaflet) sobre ortofoto PNOA/IGN y OpenStreetMap con consulta puntual a SIGPAC.
- Ficha de parcela: provincia, polígono, parcela, recinto, pendiente, altitud, elegibilidad y geometría.
- Diagnóstico climático (AEMET) e interpretación por IA.
- Propiedades hídricas del suelo a partir de rásteres locales de SoilGrids.
- Diagnóstico edafológico (ITACYL) interpretado por IA.
- Panel de evolución de la renta agraria extraído de los informes CEA/CEAS del INE en PDF.
- Calculadora de productividad plurianual con proyección compuesta y bandas de sensibilidad.
- Exportación a PDF de la ficha de parcela y del panel de rendimientos.
- Registro, login y recuperación de contraseña; la calculadora y las descargas quedan reservadas a usuarios registrados.

---

## 2. Herramientas — Qué utiliza

### Desarrollo Web y API

- **Django**: framework web de alto nivel para Python; maneja la estructura general de la aplicación, el enrutamiento, la administración y la base de datos.
- **asgiref**: interfaz de puerta de enlace de servidor asíncrono; necesaria para que Django gestione peticiones asíncronas (ASGI).
- **websockets**: biblioteca para construir servidores y clientes WebSocket, permitiendo comunicación bidireccional en tiempo real.
- **httpx / requests**: clientes HTTP para realizar peticiones a servicios o API externas (httpx soporta llamadas asíncronas).
- **python-decouple / python-dotenv**: carga de la configuración sensible desde el archivo `.env`.
- **tenacity**: reintentos controlados sobre llamadas de red inestables.

### Análisis de Datos y Ciencia

- **pandas**: herramienta fundamental para la manipulación y análisis de datos estructurados mediante tablas (DataFrames).
- **numpy**: biblioteca base para cálculo numérico masivo y operaciones con matrices o arreglos multidimensionales.
- **xarray**: extensión de NumPy orientada a datos multidimensionales etiquetados (muy usada en datos meteorológicos, satelitales y climáticos).
- **openpyxl**: lectura y escritura de hojas de cálculo en formato `.xlsx`, usado para volcar o importar tablas de datos tabulares.

### Geodatos, GIS y Mapas

- **rasterio**: manejo, lectura y escritura de imágenes satelitales y datos ráster geoespaciales. Es la pieza con la que se leen los `.tif` de SoilGrids.
- **geopy / geographiclib**: herramientas para geocodificación (convertir direcciones a coordenadas) y cálculo de distancias sobre la superficie terrestre.
- **geojson / xyzservices**: lectura/escritura del formato GeoJSON y proveedores de capas de mapas base en loseta (tiles).
- **affine**: realiza transformaciones de matrices afines, clave para mapear coordenadas de píxeles a coordenadas geográficas.
- **pyproj**: reproyección entre sistemas de referencia (EPSG:4326 ↔ EPSG:25830/3857).
- **shapely**: operaciones geométricas sobre las geometrías devueltas por SIGPAC.
- **Leaflet + Leaflet.VectorGrid + Leaflet Control Geocoder** (en el navegador): mapa, capas WMS/WMTS y buscador de lugares.

### Base de Datos y Seguridad

- **psycopg**: controlador (driver) oficial para conectar Python y Django con bases de datos PostgreSQL.
- **cryptography**: funciones criptográficas de bajo nivel para cifrado, firma de datos y manejo de claves.
- **google-auth**: gestión de autenticación e identidades para servicios de Google Cloud.

### Inteligencia artificial y modelos

- **google-genai**: SDK oficial para interactuar con los modelos de lenguaje y generación de Google (como Gemini).
- **markdown**: convierte a HTML la respuesta en Markdown que devuelven los asistentes de Gemini antes de inyectarla en la plantilla.
- **pydantic**: validación de datos y gestión de configuraciones mediante tipos de Python; ampliamente usado para estructurar respuestas de IA y API.

### Visualización y Tratamiento de Imágenes

- **matplotlib**: biblioteca principal para la creación de gráficos 2D y visualización estática de datos. Se usa para generar las imágenes de las gráficas que se incrustan en el PDF.
- **pillow (PIL)**: procesamiento, manipulación y edición de imágenes (formatos JPG, PNG, etc.).
- **Chart.js** (en el navegador): gráficas interactivas del panel de rendimientos y de la calculadora.

### Documentos y OCR

- **pytesseract**: interfaz de Python sobre Tesseract OCR; reconoce el texto de los PDF escaneados del INE.
- **pypdf / xhtml2pdf / reportlab / svglib**: lectura de PDF y generación de los informes descargables.
- **poppler-utils** (binarios del sistema `pdftotext` y `pdftoppm`): extracción de texto nativo y rasterizado de páginas previo al OCR.

---

## 3. Requisitos e instalación

### Dependencias del sistema

Además de los paquetes de Python, el equipo o la imagen necesita:

- `poppler-utils` → aporta `pdftotext` y `pdftoppm`, invocados por `ine/services/extractor.py`.
- `tesseract-ocr` y `tesseract-ocr-spa` → OCR en español para los informes escaneados.
- `libexpat1`, `gdal` y librerías geoespaciales que requiere `rasterio`.
- PostgreSQL 16 (o el contenedor `db` del `docker-compose.yml`).

### Instalación local

```bash
git clone <url-del-repositorio>
cd pulso-rural

python -m venv .venv
source .venv/bin/activate        # En Windows: .venv\Scripts\activate

pip install -r requirements.txt

cp .env.example .env             # y rellenar las claves
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

### Instalación con Docker

```bash
docker compose up --build
docker compose exec web python manage.py migrate
docker compose exec web python manage.py createsuperuser
```

Servicios que levanta el `docker-compose.yml`:

| Servicio | Contenedor | Puerto |
| --- | --- | --- |
| Django | `django_web` | 8000 |
| PostgreSQL 16 | `postgres_db` | 5433 |
| pgAdmin | `pgadmin` | 5050 |

### Variables de entorno (`.env`)

Las lee `config/entorno.py` y las consume `config/settings.py`.

```dotenv
SECRET_KEY=clave-secreta-de-django
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

DB_NAME=pulsorural
DB_USER=postgres
DB_PASSWORD=contrasena
DB_HOST=db
DB_PORT=5432

AEMET_API_KEY=clave-de-aemet-opendata
API_KEY_GEMINI=clave-de-google-gemini
```

### Datos que deben existir en disco

- `ine/datos/pdfs/` → informes CEA/CEAS del INE en PDF (2010–2023). Es la fuente que procesa el microsistema de `ine/services`.
- `solgrids/data/soilgrids/` → rásteres `.tif` de SoilGrids (`clay_mean`, `sand_mean`, `wv0033_mean`, `wv1500_mean` por tramos de profundidad 0-5, 5-15 y 15-30 cm).

---

## 4. Estructura del proyecto

```text
pulso-rural/
├── config/              Ajustes, URLs raíz, WSGI/ASGI y carga del .env
├── core/                Página de inicio y clases base de servicios
├── sigpac/              Consulta puntual y por área al visor SIGPAC
├── aemet/               Clima de estaciones AEMET OpenData + IA
├── solgrids/            Propiedades hídricas leídas de rásteres SoilGrids
├── itacyl/              Datos edafológicos de ITACYL + IA
├── ine/                 Renta agraria extraída de PDFs del INE + analíticas + IA
├── calculadora/         Cálculo de márgenes y proyección plurianual
├── usuarios/            Registro, login, recuperación y permisos
├── templates/           Plantillas HTML (base, componentes, una carpeta por app)
├── static/              CSS, JS e imágenes
├── requirements.txt
├── Dockerfile
└── docker-compose.yml
```

---

## 5. Arquitectura — Modelo de extracción e interpretación

Hay dos patrones distintos según el origen del dato.

### 5.1.1 Fuentes en línea (SIGPAC, AEMET, SoilGrids, ITACYL)

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
     |    Service      |          |  Gemini Service  |
     |   (Extracción)  |          |  (Interpretación)|
     +-----------------+          +------------------+
```
### 5.1.2 Fuentes en línea (INE)
```text
+---------------------------------------------------------------+
|                      Vista / Controller                       |
+---------------------------------------------------------------+
       |                                                 ^
       | 1. Solicita análisis de una zona / archivo      | 6. Retorna resultado
       v                                                 |    final listo
+---------------------------------------------------------------+
|                        agregador.py                           |
|                    (Orquestador Principal)                    |
+---------------------------------------------------------------+
       |                                                 ^
       | 2. Lee archivos desde                           | 5. Devuelve análisis
       |    datos/pdfs/ y procesa                        |    + JSON estructurado
       v                                                 |
+-------------------------------+               +---------------+
|      services/ (Carpeta)      |               | gemini_services.py
|  - orchestrator.py            |               | (Envía JSON a |
|  - extractor.py (Lee de disco)|               |  la API de IA)|
|  - paser.py (Genera JSON)     |               +---------------+
+-------------------------------+                       ^
       |                                                |
       +---- 3. Lee de datos/pdfs/ y -------------------+
             guarda en datos/salida_json/

```

El contrato común lo define `core/base_services.py`: cada servicio implementa `fetch()` (traer el dato crudo) y `normalize()` (dejarlo en un diccionario estable), y el método `get_data()` encadena ambos capturando cualquier excepción para que un fallo de una fuente externa nunca rompa la vista.

### 5.2 Fuentes documentales (CEAS)

```text
ine/
│
├── services/
│   ├── __init__.py
│   ├── extractor.py     <-- 1. Lectura de PDFs e imágenes (OCR)
│   ├── paser.py         <-- 2. Lógica de expresiones regulares y parseo de tablas
│   └── orchestrator.py  <-- 3. Orquestador principal (conecta extractor y parser)
│
```

> Nota: el archivo se llama `paser.py` (no `parser.py`). Es una errata de nombre que se mantiene porque `orchestrator.py` y el resto del código ya importan de ella; si se renombra, hay que actualizar esos imports.

---

## 6. Módulos — Qué hace cada archivo

### 6.1 `config/`

| Archivo | Función |
| --- | --- |
| `entorno.py` | Carga el `.env` con `dotenv` y expone `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`, credenciales de PostgreSQL, `AEMET_API_KEY` y `API_KEY_GEMINI`. Centraliza el acceso a secretos para que `settings.py` no lea variables de entorno directamente. |
| `settings.py` | Configuración de Django: apps instaladas, base de datos PostgreSQL, plantillas, idioma `es-es`, zona horaria `Europe/Madrid`, estáticos y correo. |
| `urls.py` | Enrutador raíz. Monta cada app bajo su prefijo: `/`, `/sigpac/`, `/aemet/`, `/solgrids/`, `/itacyl/`, `/ine/`, `/usuarios/`, `/calculadora/`. |
| `wsgi.py` / `asgi.py` | Puntos de entrada del servidor síncrono y asíncrono. |

### 6.2 `core/` — cimientos

| Archivo | Función |
| --- | --- |
| `base_services.py` | Define `BaseDataService` (firma fija `fetch(lat, lng)` / `normalize(raw)` y el `get_data()` que los encadena con captura de errores) y `BaseDataServiceINE` (misma idea pero con `**kwargs`, para fuentes que no se consultan por coordenadas). Es la clase de la que heredan SIGPAC, AEMET, SoilGrids e ITACYL. |
| `views.py` | Vista `inicio`, la portada del sitio. |
| `urls.py` | Ruta `''` → `inicio`. |

### 6.3 `sigpac/` — Sistema de Información Geográfica de Parcelas Agrícolas

Es la aplicación encargada de llamar al SIGPAC, solicitar los datos del registro de la parcela seleccionada en el mapa y mostrarlos. Se resume en consulta puntual y extracción de los metadatos y la geometría.

| Archivo | Función |
| --- | --- |
| `service.py` | Contiene dos servicios. `SigpacPuntoService`: recibe latitud/longitud de un clic, consulta el recinto que contiene ese punto y en `normalize()` extrae provincia, municipio, polígono, parcela, recinto, uso, superficie, pendiente media y la geometría GeoJSON; el helper `_obtener_primer_valor()` tolera que el servicio de origen cambie el nombre de las claves. `SigpacAreaService`: consulta por cuadro delimitador (bounding box) con un límite de resultados, para pintar varios recintos de una zona. Cuando no hay recinto bajo el punto, devuelve la marca `sin_recinto` que la plantilla usa para avisar al usuario. |
| `views.py` | `mapa` renderiza `templates/sigpac/mapa.html`; `croquis_parcela` responde en JSON a los clics del mapa con la ficha del recinto; `descargar_pdf_parcela` compone el informe descargable de la parcela. |
| `urls.py` | `mapa/`, `croquis/`, `descargar_pdf_parcela/`. |

### 6.4 `aemet/` — Agencia Estatal de Meteorología

Esta fuente tiene el siguiente sistema:

```text
[PULSORURAL] ---> 1. GET (URL API + api_key) ---> [AEMET OpenData]
[PULSORURAL] <--- 2. JSON { "datos": "https://..." } <--- [AEMET OpenData]
[PULSORURAL] ---> 3. GET (URL temporal) ---------> [Servidor de Datos AEMET]
[PULSORURAL] <--- 4. JSON con los datos crudos <--- [Servidor de Datos AEMET]
```

El punto de origen de la petición es un clic en el mapa, por tanto el sistema debe resolver la ubicación desde la que se solicitan los datos. Cuenta con una estrategia de reserva (*fallback*) de cinco intentos en la que busca las cinco estaciones más cercanas al punto, reduciendo las posibilidades de retornar datos nulos.

La web está diseñada para cargar datos al vuelo, por tanto el inventario completo de estaciones se almacena en memoria/Redis (`cache.set`) durante 24 horas (`CACHE_TTL_INVENTARIO_SEGUNDOS`) para evitar descargar la lista de estaciones en cada llamada. Asimismo, el método `normalize()` toma los datos devueltos por AEMET (`datos_brutos`) y corrige las inconsistencias del formato de origen.

| Archivo | Función |
| --- | --- |
| `aemet_services.py` | Clase `Aemet(BaseDataService)`. `_obtener_inventario_estaciones()` descarga y cachea 24 h la lista de estaciones bajo la clave `aemet_inventario_estaciones`. `_coordenada_dms_a_decimal()` convierte las coordenadas en grados-minutos-segundos del inventario a decimal. `_distancia_haversine_km()` y `_estaciones_ordenadas_por_cercania()` ordenan las estaciones por proximidad al punto clicado. `fetch()` recorre hasta `MAX_ESTACIONES_A_INTENTAR` (5) estaciones hasta obtener datos no vacíos, resolviendo los dos saltos de URL que exige AEMET OpenData. `normalize()` homogeneiza tipos, decimales con coma y valores ausentes. |
| `gemini_services.py` | `asistente_virtual(contexto_negocio)`: envía el resumen climático ya normalizado a Gemini con una instrucción de sistema agronómica y devuelve el diagnóstico redactado. |
| `agregador.py` | Clase `ClimaInteligenteAggregator`. Su método `obtener_analisis_completo()` es la fachada: pide el dato al servicio, se lo pasa al asistente de Gemini y devuelve un único objeto con datos + interpretación. Acepta `identificador_estacion`, coordenadas, año, mes y `forzar_regeneracion` para saltarse la caché del análisis. |
| `views.py` | `api_diagnostico_clima`: endpoint JSON que consume el JavaScript del mapa. |
| `urls.py` | `consulta_clima/`. |

### 6.5 `solgrids/` — SoilGrids (propiedades hídricas)

A diferencia del resto, esta fuente no se consulta por red: los rásteres de SoilGrids están descargados en `solgrids/data/soilgrids/` y se leen en local, lo que la hace inmune a caídas del servicio externo.

| Archivo | Función |
| --- | --- |
| `solgrids_services.py` | Clase `PropiedadesHidricas(BaseDataService)`. `_leer_pixel_raster()` abre cada `.tif` con rasterio, reproyecta la coordenada y lee el valor del píxel correspondiente. `fetch()` recopila, para las profundidades 0-5, 5-15 y 15-30 cm, el contenido de arcilla (`clay_mean`), de arena (`sand_mean`), la capacidad de campo (`wv0033_mean`) y el punto de marchitez (`wv1500_mean`). `normalize()` aplica los factores de escala de SoilGrids, calcula el agua disponible para la planta (capacidad de campo menos punto de marchitez) y devuelve la textura y la retención hídrica por horizonte. |
| `views.py` | `api_diagnostico_aguas`: endpoint JSON que inyecta la tarjeta hídrica en el mapa. |
| `urls.py` | `consulta_aguas/`. |
| `data/soilgrids/` | Rásteres GeoTIFF de origen. |

### 6.6 `itacyl/` — Instituto Tecnológico Agrario de Castilla y León

| Archivo | Función |
| --- | --- |
| `itacyl_services.py` | Clase `Suelos(BaseDataService)`. `fetch(lat, lng, anio, mes)` consulta el servicio de ITACYL para el punto y el periodo indicados; `normalize()` deja las propiedades edafológicas en un diccionario estable para la plantilla y para el prompt de IA. |
| `gemini_services.py` | `asistente_virtual(contexto_negocio)`: interpreta el bloque de suelo y devuelve un diagnóstico agronómico legible. |
| `views.py` | `api_diagnostico_suelo`: endpoint JSON que rellena la tarjeta «Datos de Suelo» del mapa. |
| `urls.py` | `consulta_suelos/` (nombre de ruta `itacyl:consulta_suelo`). |

### 6.7 `ine/` — Instituto Nacional de Estadística / renta agraria

Es la app más compleja porque la fuente no es una API, sino una colección de informes CEA/CEAS en PDF de distintos años y maquetados de forma distinta. Por eso incorpora un microsistema propio de extracción documental.

#### El microsistema `ine/services/`

Es una tubería de tres etapas, cada una con una única responsabilidad, de modo que se puede cambiar el motor de lectura sin tocar el parseo y al revés.

```text
PDF / imagen
     │
     ▼
[1] extractor.py  ──► texto plano
     │              (pdftotext -layout; si el texto es
     │               insuficiente, pdftoppm + Tesseract)
     ▼
[2] paser.py      ──► diccionario anidado A..H
     │              (expresiones regulares sobre la tabla
     │               de Renta Agraria)
     ▼
[3] orchestrator.py ──► {archivo_origen, anio, moneda,
                         unidad, tabla_resultados_renta_agraria}
```

| Archivo | Función detallada |
| --- | --- |
| `extractor.py` | **Etapa 1: convertir cualquier archivo en texto plano.** `extraer_texto_archivo()` mira la extensión y decide la estrategia. Si es imagen (`.png`, `.jpg`, `.jpeg`, `.tif`, `.tiff`, `.bmp`) llama a `_extraer_texto_imagen_ocr()`, que aplica Tesseract con los idiomas `spa+eng`. Si es PDF, primero prueba `_extraer_texto_pdf_nativo()`, que ejecuta `pdftotext -layout` — el flag `-layout` es esencial porque conserva la separación en columnas de las tablas, y sin ella el parseo posterior sería imposible. Si el resultado tiene menos de `MINIMO_CARACTERES_TEXTO_NATIVO` (200 caracteres), asume que el PDF es un escaneo sin capa de texto y recurre a `_extraer_texto_pdf_escaneado_ocr()`, que rasteriza cada página a JPEG a 200 ppp con `pdftoppm` en un directorio temporal, pasa Tesseract página a página y concatena el resultado. Cualquier otra extensión lanza `ValueError`. Esta detección automática es lo que permite mezclar en la misma carpeta informes modernos digitales e informes antiguos escaneados. |
| `paser.py` | **Etapa 2: convertir el texto plano en una estructura jerárquica.** `parsear_tabla_resultados()` localiza la tabla usando dos anclas (`A. Producción rama agraria` como inicio y `H. Renta agraria` como fin) y solo analiza las líneas entre ambas, ignorando portadas, notas y anexos. Cada línea se contrasta con `PATRON_LINEA_TABLA`, que reconoce el formato «etiqueta + dos o más espacios + importe + porcentaje opcional». `_convertir_texto_a_flotante()` traduce el formato numérico español (`1.234,56` → `1234.56`) y `_extraer_porcentaje()` recupera la columna de la derecha si existe. A partir de ahí reconstruye la jerarquía en cuatro niveles: las categorías `A`–`H` mediante `PATRON_NIVEL_SUPERIOR`; las subsecciones de la producción agraria (`producción vegetal`, `producción animal`, `producción de servicios`, `otras producciones`) mediante el conjunto `SUBSECCIONES_BAJO_A`; los bloques ganaderos (`carne y ganado`, `productos animales`); y por último las filas numeradas de detalle con `PATRON_FILA_NUMERADA`, que se cuelgan del nodo abierto más profundo. `_normalizar_etiqueta()` unifica espacios, mayúsculas y puntos finales para que las comparaciones funcionen entre maquetaciones de años distintos. Si no encuentra las anclas devuelve `{"encontrada": False, "items": []}` en lugar de fallar. También expone `extraer_anio_informe()`, que deduce el ejercicio a partir del propio texto y, como último recurso, del nombre del archivo. |
| `orchestrator.py` | **Etapa 3: coordinar y estandarizar la salida.** `procesar_archivo_ceas()` encadena extractor y parser sobre un archivo y envuelve el resultado en un sobre homogéneo: `archivo_origen`, `anio`, `moneda` (`EUR`), `unidad` (`millones`) y `tabla_resultados_renta_agraria`. `procesar_directorio_ceas()` recorre una carpeta, filtra por extensiones válidas, ordena los archivos y devuelve la lista de informes procesados. Es la única función que el resto del proyecto necesita conocer: nadie fuera de `services/` importa el extractor ni el parser. |

#### Resto de la app INE

| Archivo | Función |
| --- | --- |
| `agregador.py` | Clase `IneAgregador`, fachada de la app. `obtener_datos_base()` lee la carpeta `ine/datos/pdfs`, la procesa con `procesar_directorio_ceas()`, ordena los informes por año descendente y genera los datos de gráfica con el disparador; deliberadamente **no** llama a Gemini, porque su salida está pensada para cachearse en sesión en la carga inicial. `generar_informe_ia()` se invoca después, bajo demanda, y ejecuta solo el asistente que el usuario haya elegido según el diccionario `ASISTENTES`. Ambos métodos devuelven siempre `{"estado": "ok"|"error", ...}`, de modo que la vista nunca tiene que gestionar excepciones. |
| `analiticas/disparador.py` | Punto único de entrada a las gráficas: `disparador_analitica(tipo_grafica, lista_informes)`. Con `"panel_completo"` devuelve de golpe las cuatro series (`vegetal`, `animal`, `evolucion_global`, `provincial_anio`); con un tipo desconocido lanza `ValueError`. Añadir una gráfica nueva consiste en escribir su función y registrarla aquí. |
| `analiticas/evolucion.py` | `datos_produccion_vegetal()` y `datos_produccion_animal()` recorren los informes de todos los años y construyen las series temporales plurianuales de cada rama. |
| `analiticas/provinciales.py` | `evolucion_global()` arma la serie histórica agregada de la comunidad; `desglose_provincial_anio()` prepara el reparto por cultivos de un año concreto para el gráfico de sectores. |
| `gemini_services.py` | Cuatro asistentes con distinta instrucción de sistema sobre el mismo conjunto de datos: `asistente_virtual` (lectura general), `asistente_crecimiento`, `asistente_financiero` y `asistente_desarrollo`. `_consultar_gemini()` centraliza la llamada y recorre `MODELOS_INTENTAR` (`gemini-3.6-flash`, `gemini-2.5-flash`) para degradar a un modelo alternativo si el primero no está disponible. |
| `views.py` | `vista_evolucion_agraria` renderiza el panel y, cuando llega el parámetro `informe`, responde en JSON con el análisis de IA cacheado en sesión. `generar_imagen_barras`, `generar_imagen_torta` y `generar_imagen_lineas` rasterizan las gráficas con matplotlib para poder incrustarlas en el PDF, y `descargar_pdf` compone el informe descargable. |
| `urls.py` | `rendimientos/` y `rendimientos/descargar-pdf/`. |
| `datos/pdfs/` | Informes CEA/CEAS de origen. |
| `datos/salida_json/rendimiento_datos.json` | Volcado de la última extracción, útil para inspeccionar el resultado del parseo sin reprocesar los PDF. |

### 6.8 `calculadora/` — productividad plurianual

| Archivo | Función |
| --- | --- |
| `views.py` | `calcular`: recibe por GET `superficie_ha`, `rendimiento_kg_ha`, `precio_kg`, `coste_ha`, `anios` y `tasa_interes`, valida los tipos y devuelve producción, ingreso, coste, margen total y margen por hectárea. Si se pasan varios años, aplica crecimiento compuesto `(1 + tasa)^i` sobre precio y coste y devuelve la lista `proyeccion`. `calcular_grafica_comparativa`: con los mismos parámetros, devuelve el objeto `chart` listo para Chart.js con la serie base y las bandas de sensibilidad del +2 % y el −2 %. `asistente_calculadora`: renderiza la plantilla del mapa. Todas las vistas de cálculo están protegidas con `@login_required`. |
| `urls.py` | `calculadora/`, `grafica_comparativa/`, `asistente_calcularoas/`. |

### 6.9 `usuarios/` — acceso y permisos

| Archivo | Función |
| --- | --- |
| `views.py` | `register`: alta de usuarios nuevos. |
| `urls.py` | Login, logout y el ciclo completo de recuperación de contraseña apoyándose en las vistas de `django.contrib.auth` con plantillas propias. |
| `decorator.py` | `requiere_permiso(codigo_permiso)`: decorador que restringe una vista a los usuarios que tengan el permiso indicado. |
| `templatetags/auth_extras.py` | Filtro `is_gestor(user)` para condicionar bloques de plantilla al rol de gestor. |

### 6.10 `static/` y `templates/`

| Archivo | Función |
| --- | --- |
| `static/js/mapa.js` | `inicializarMapaSigpac()`: monta Leaflet, las capas base (OSM y PNOA/IGN), la capa de recintos SIGPAC, el buscador de lugares y el manejador de clics que llama en cadena a `croquis`, `consulta_aguas` y `consulta_suelo`. |
| `static/js/calculadora.js` | Escucha el botón de calcular por delegación en `document`, arma la query con `URLSearchParams`, rellena el panel de resultados con el último año de la proyección y dibuja la gráfica con Chart.js mediante `renderizarGrafica()`. |
| `static/js/pdf_mapa.js` | Exporta a PDF la ficha completa del mapa con html2pdf. |
| `static/js/rendimientos.js` | Interacción del panel del INE: cambio de gráfica y petición del informe de IA elegido. |
| `static/css/mapa.css` | Estilos del contenedor del mapa, la leyenda y las tarjetas de datos. |
| `static/css/pdf_redimientos.css` | Estilos del PDF de rendimientos. *(El nombre contiene una errata: `redimientos`. La referencia en `base.html` debe coincidir exactamente con este nombre o el archivo dará 404.)* |
| `templates/base.html` | Plantilla madre: cabecera, Bootstrap, Leaflet, Chart.js, navbar, footer, modal de bienvenida y los bloques `title`, `extra_css`, `contenido` y `extra_js`. |
| `templates/sigpac/mapa.html` | Pantalla principal: mapa, leyenda, tarjetas de recinto, hídrica, suelo y clima, y la calculadora. |
| `templates/ine/rendimientos.html` | Panel de evolución de la renta agraria. |
| `templates/componentes/` | Navbar y footer reutilizables. |

---

## 7. Rutas principales

| URL | Nombre | Descripción |
| --- | --- | --- |
| `/` | `inicio` | Portada |
| `/sigpac/mapa/` | `mapa` | Mapa y consulta de parcela |
| `/sigpac/croquis/` | `croquis` | JSON de la ficha del recinto |
| `/sigpac/descargar_pdf_parcela/` | `descargar_pdf_parcela` | PDF de la parcela |
| `/aemet/consulta_clima/` | `consulta_clima` | JSON de clima + diagnóstico IA |
| `/solgrids/consulta_aguas/` | `consulta_aguas` | JSON de propiedades hídricas |
| `/itacyl/consulta_suelos/` | `itacyl:consulta_suelo` | JSON de suelo + diagnóstico IA |
| `/ine/rendimientos/` | `rendimientos` | Panel de renta agraria |
| `/ine/rendimientos/descargar-pdf/` | `pdf_rendimientos` | PDF del panel |
| `/calculadora/calculadora/` | `calculadora` | Cálculo de márgenes y proyección |
| `/calculadora/grafica_comparativa/` | `grafica_comparativa` | Series para la gráfica |
| `/usuarios/login/` | `login` | Acceso |
| `/usuarios/register/` | `register` | Registro |

---

## 8. Pendientes conocidos

- `paser.py` debería llamarse `parser.py`; el renombrado implica actualizar el import de `orchestrator.py`.
- `static/css/pdf_redimientos.css` tiene una errata en el nombre del archivo.
- `STATIC_URL` está definido como `'static/'`; conviene dejarlo como `'/static/'`.
- `calculadora.js` solo consulta la vista `calculadora`, que no devuelve la clave `chart`; la gráfica requiere una segunda petición a `grafica_comparativa` o fusionar ambas vistas.
- `ine/datos/pdfs` se procesa en cada arranque de la vista; conviene persistir el resultado en base de datos o en `datos/salida_json/`.
- No hay batería de tests: los archivos `tests.py` de cada app están vacíos.
