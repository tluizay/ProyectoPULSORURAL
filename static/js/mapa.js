// static/js/mapa.js

function inicializarMapaSigpac(config) {
    document.addEventListener("DOMContentLoaded", function () {
        // Coordenadas por defecto inyectadas desde Django
        const latitudPorDefecto = Number(config.latitud);
        const longitudPorDefecto = Number(config.longitud);

        // 1. Definir las capas base (Satélite PNOA y Calles OpenStreetMap)
        const ortofotoPNOA = L.tileLayer.wms("https://www.ign.es/wms-inspire/pnoa-ma", {
            layers: 'OI.OrthoimageCoverage',
            format: 'image/jpeg',
            transparent: false,
            version: '1.3.0',
            attribution: '© PNOA / IGN',
            maxZoom: 20
        });

        const capaOpenStreetMap = L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
            maxZoom: 19,
            attribution: '&copy; OpenStreetMap'
        });

        // 2. Inicializar el mapa y reubicar los botones de zoom abajo a la derecha
        const mapa = L.map('contenedor-mapa', {
            doubleClickZoom: false,
            zoomControl: false, // Quitamos el control por defecto de arriba a la izquierda
            layers: [ortofotoPNOA]
        }).setView([latitudPorDefecto, longitudPorDefecto], 16);

        // Colocar los botones de zoom en la esquina inferior derecha
        L.control.zoom({
            position: 'bottomright'
        }).addTo(mapa);

        // 3. BARRA DE BÚSQUEDA DE CIUDADES/PROVINCIAS EN EL MAPA
        try {
            const controlBuscador = L.Control.geocoder({
                position: 'topleft',
                collapsed: false,
                defaultMarkGeocode: true,
                placeholder: "Buscar ciudad, provincia o lugar...",
                errorMessage: "No se ha encontrado el lugar.",
                geocoder: L.Control.Geocoder.nominatim({
                    geocodersParams: {
                        countrycodes: 'es'
                    }
                })
            }).addTo(mapa);

            controlBuscador._container.classList.add('buscador-lugares-grande');
        } catch (errorGeocoder) {
            console.error("No se pudo iniciar el buscador de lugares:", errorGeocoder);
        }

        // 4. Capas superpuestas (Límites de Catastro y Recintos SIGPAC)
        const capaCatastro = L.tileLayer.wms("https://ovc.catastro.meh.es/cartografia/wms/servidor.aspx", {
            layers: 'CP.CadastralParcel',
            format: 'image/png',
            transparent: true,
            version: '1.1.1',
            attribution: '© Dirección General del Catastro',
            maxZoom: 20,
            zIndex: 50
        }).addTo(mapa);

        const capaSigpacRecintos = L.tileLayer.wms("https://sigpac-hubcloud.es/wms/ows", {
            layers: 'AU.Sigpac:recinto',
            format: 'image/png',
            transparent: true,
            version: '1.3.0',
            attribution: '© SIGPAC',
            maxZoom: 20,
            zIndex: 100
        }).addTo(mapa);

        // 5. Configurar el control de capas
        const mapasBase = {
            "Satélite (PNOA)": ortofotoPNOA,
            "Calles (OpenStreetMap)": capaOpenStreetMap
        };

        const capasSuperpuestas = {
            "Límites Catastro (Rojas)": capaCatastro,
            "Recintos SIGPAC": capaSigpacRecintos
        };

        L.control.layers(mapasBase, capasSuperpuestas, {
            position: 'topright',
            collapsed: false
        }).addTo(mapa);

        setTimeout(() => {
            mapa.invalidateSize();
        }, 200);

        // 6. Renderizar parcela seleccionada (Morado)
        const nodoGeometria = document.getElementById('geometria-data');

        if (nodoGeometria && nodoGeometria.textContent.trim() !== "" && nodoGeometria.textContent.trim() !== "null") {
            try {
                let datosGeoJson = JSON.parse(nodoGeometria.textContent);

                if (typeof datosGeoJson === 'string') {
                    datosGeoJson = JSON.parse(datosGeoJson);
                }

                const estructuraValida = datosGeoJson.geometry || datosGeoJson;

                if (estructuraValida && (estructuraValida.coordinates || estructuraValida.features || estructuraValida.type)) {
                    const capaPoligono = L.geoJSON(estructuraValida, {
                        style: {
                            color: '#6f42c1',
                            weight: 4,
                            opacity: 0.9,
                            fillColor: '#a855f7',
                            fillOpacity: 0.45
                        }
                    }).addTo(mapa);

                    const limites = capaPoligono.getBounds();
                    if (limites.isValid()) {
                        mapa.fitBounds(limites, { padding: [30, 30] });
                    }
                }
            } catch (error) {
                console.error("Error al procesar el GeoJSON en Leaflet:", error);
            }
        }

        // 7. Manejo de Clics usando la URL inyectada
        mapa.on('click', function (evento) {
            const latitudSeleccionada = evento.latlng.lat;
            const longitudSeleccionada = evento.latlng.lng;
            window.location.href = `${config.urlCroquis}?lat=${latitudSeleccionada}&lon=${longitudSeleccionada}`;
        });

        // 8. Peticiones asíncronas (Clima, Hídrico, Suelo) usando coordenadas limpias
        const lat = config.lat.replace(',', '.');
        const lon = config.lon.replace(',', '.');

        // A. AEMET
        fetch(`/aemet/consulta_clima/?lat=${lat}&lon=${lon}`)
            .then(response => {
                if (!response.ok) throw new Error("Error en la respuesta del servidor AEMET");
                return response.json();
            })
            .then(data => {
                const contenedorIa = document.getElementById('contenedor-diagnostico-ia');
                if (!contenedorIa) return;
                const infoIa = data.interpretacion_ia || {};
                const texto = infoIa.interpretacion_ia || infoIa.error || data.mensaje;
                if (texto) {
                    contenedorIa.innerHTML = `<div class="caja-diagnostico-ia">${texto}</div>`;
                }
            })
            .catch(err => console.error("Error al cargar AEMET:", err));

        // B. SoilGrids (Hídrico)
        const contenedorHidrico = document.getElementById('contenedor-hidrico');
        if (contenedorHidrico) {
            contenedorHidrico.innerHTML = `
                <div class="card p-3 shadow-sm border-0 bg-white h-100 tarjeta-datos">
                    <h5 class="mb-2 text-primary"><i class="bi bi-droplet-half"></i> Datos Hídricos</h5>
                    <p class="text-info small mb-0">Consultando propiedades hídricas del suelo...</p>
                </div>`;
        }

        fetch(`${config.urlAguas}?lat=${lat}&lon=${lon}`)
            .then(response => {
                if (!response.ok) throw new Error("Error en la respuesta hídrica");
                return response.json();
            })
            .then(data => {
                if (!contenedorHidrico) return;
                if (data.datos_disponibles) {
                    contenedorHidrico.innerHTML = `
                        <div class="card p-3 bg-white border-start border-primary border-3 shadow-sm h-100 tarjeta-datos">
                            <h5 class="fw-bold text-primary mb-2"><i class="bi bi-droplet-half"></i> Propiedades Hídricas (SoilGrids)</h5>
                            <p class="mb-1 small"><strong>Capacidad de Campo:</strong> ${data.capacidad_campo ?? 'N/D'} %</p>
                            <p class="mb-1 small"><strong>Punto de Marchitez:</strong> ${data.punto_marchitez ?? 'N/D'} %</p>
                            <p class="mb-1 small"><strong>Agua Útil:</strong> ${data.agua_util ?? 'N/D'} %</p>
                            <p class="mb-0 small"><strong>Profundidad Útil:</strong> ${data.profundidad_util_centimetros ?? 'N/D'} cm</p>
                        </div>
                    `;
                } else {
                    contenedorHidrico.innerHTML = `
                        <div class="card p-3 bg-white border-0 shadow-sm h-100 tarjeta-datos">
                            <h5 class="mb-2 text-primary"><i class="bi bi-droplet-half"></i> Datos Hídricos</h5>
                            <p class="text-muted mb-0 small">Sin datos hídricos disponibles para esta ubicación.</p>
                        </div>`;
                }
            })
            .catch(err => {
                console.error("Error hídrico:", err);
                if (contenedorHidrico) contenedorHidrico.innerHTML = `
                    <div class="card p-3 bg-white border-0 shadow-sm h-100 tarjeta-datos">
                        <h5 class="mb-2 text-primary"><i class="bi bi-droplet-half"></i> Datos Hídricos</h5>
                        <p class="text-danger mb-0 small">⚠️ No se pudo cargar el diagnóstico hídrico.</p>
                    </div>`;
            });

        // C. ITACYL + Gemini (Suelos)
        const contenedorSuelos = document.getElementById('contenedor-diagnostico-suelo');
        if (contenedorSuelos) {
            contenedorSuelos.innerHTML = `
                <div class="card p-3 shadow-sm border-0 bg-white h-100 tarjeta-datos">
                    <h5 class="mb-2 text-success"><i class="bi bi-flower1"></i> Diagnóstico de Suelos</h5>
                    <p class="text-info small mb-0">Consultando tipo de suelo e informe agronómico...</p>
                </div>`;
        }

        fetch(`${config.urlSuelos}?lat=${lat}&lon=${lon}`)
            .then(response => {
                if (!response.ok) throw new Error("Error en suelos ITACYL");
                return response.json();
            })
            .then(data => {
                if (!contenedorSuelos) return;
                if (data.error) {
                    contenedorSuelos.innerHTML = `
                        <div class="card p-3 bg-white border-0 shadow-sm h-100 tarjeta-datos">
                            <h5 class="mb-2 text-success"><i class="bi bi-flower1"></i> Diagnóstico de Suelos</h5>
                            <p class="text-danger small mb-0">⚠️ ${data.error}</p>
                        </div>`;
                    return;
                }
                const municipio = data.nombre_municipio || 'No especificado';
                const interpretacionIa = data.interpretacion_ia || 'Sin análisis disponible.';

                contenedorSuelos.innerHTML = `
                    <div class="card p-3 bg-white border-start border-success border-4 shadow-sm h-100 tarjeta-datos">
                        <h5 class="fw-bold text-success mb-2"><i class="bi bi-flower1"></i> Diagnóstico de Suelos (ITACYL & Gemini)</h5>
                        <p class="mb-2 small"><strong>Municipio:</strong> ${municipio}</p>
                        <div class="caja-diagnostico-ia mt-2 p-2 bg-white rounded border small text-dark">
                            ${interpretacionIa}
                        </div>
                    </div>
                `;
            })
            .catch(err => {
                console.error("Error suelos:", err);
                if (contenedorSuelos) contenedorSuelos.innerHTML = `
                    <div class="card p-3 bg-white border-0 shadow-sm h-100 tarjeta-datos">
                        <h5 class="mb-2 text-success"><i class="bi bi-flower1"></i> Diagnóstico de Suelos</h5>
                        <p class="text-danger mb-0 small">⚠️ No se pudo obtener la información del suelo.</p>
                    </div>`;
            });
    });
}