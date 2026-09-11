
document.addEventListener("DOMContentLoaded", function () {
        const loadingIndicator = document.getElementById('loadingIndicator');
        const chartsContainer = document.getElementById('chartsContainer');

        try {
            const elPanel = document.getElementById('json-datos-panel');
            if (elPanel && elPanel.textContent.trim()) {
                const data = JSON.parse(elPanel.textContent);
                
                // Inicialización de Gráfica Vegetal
                const canvasVegetal = document.getElementById('graficoVegetal');
                if (canvasVegetal && data.vegetal) {
                    new Chart(canvasVegetal.getContext('2d'), {
                        type: 'bar',
                        data: data.vegetal,
                        options: { responsive: true, maintainAspectRatio: false }
                    });
                }

                // Inicialización de Gráfica Animal
                const canvasAnimal = document.getElementById('graficoAnimal');
                if (canvasAnimal && data.animal) {
                    new Chart(canvasAnimal.getContext('2d'), {
                        type: 'bar',
                        data: data.animal,
                        options: { responsive: true, maintainAspectRatio: false }
                    });
                }

                // Inicialización de Gráfica de Líneas (Evolución Global)
                const canvasEvolucion = document.getElementById('chartEvolucionGlobal');
                if (canvasEvolucion && data.evolucion_global) {
                    new Chart(canvasEvolucion.getContext('2d'), {
                        type: 'line',
                        data: data.evolucion_global,
                        options: {
                            responsive: true,
                            maintainAspectRatio: false,
                            plugins: { legend: { position: 'top' } },
                            scales: {
                                y: {
                                    beginAtZero: true,
                                    title: { display: true, text: 'Millones de Euros' }
                                }
                            }
                        }
                    });
                }

                // Inicialización de Gráfica de Torta (Distribución)
                const canvasProvincial = document.getElementById('chartProvincialAnio');
                if (canvasProvincial && data.provincial_anio) {
                    new Chart(canvasProvincial.getContext('2d'), {
                        type: 'pie',
                        data: data.provincial_anio,
                        options: {
                            responsive: true,
                            maintainAspectRatio: false,
                            plugins: { 
                                legend: { position: 'right' } 
                            }
                        }
                    });
                }
            }

            if (loadingIndicator) loadingIndicator.style.display = 'none';
            if (chartsContainer) chartsContainer.style.display = 'block';

        } catch (error) {
            console.error("Error al renderizar las gráficas:", error);
            if (loadingIndicator) {
                loadingIndicator.innerHTML = `
                    <div class="alert alert-warning shadow-sm">
                        <i class="bi bi-info-circle me-2"></i> Ocurrió un error al cargar las gráficas. Revisa la consola para más detalles.
                    </div>`;
            }
        }
    });

   document.addEventListener("DOMContentLoaded", function () {
    const selector = document.getElementById('selectorInformeIA');
    const contenedorInforme = document.getElementById('contenidoInformeIA');
    const loadingInforme = document.getElementById('loadingInformeIA');
    const btnDescargarPdf = document.getElementById('btnDescargarPdf');

    if (!selector) return;

    // 1. Evento para actualizar el informe de forma dinámica al cambiar la opción del selector
    selector.addEventListener('change', function () {
        const tipoInforme = selector.value;
        if (!tipoInforme) return;

        // Estado de carga
        if (contenedorInforme) contenedorInforme.innerHTML = '';
        if (loadingInforme) loadingInforme.style.display = 'block';
        selector.disabled = true;

        fetch(`?informe=${encodeURIComponent(tipoInforme)}`, {
            headers: { 'X-Requested-With': 'XMLHttpRequest' }
        })
            .then(response => response.json().then(data => ({ status: response.status, data })))
            .then(({ status, data }) => {
                if (loadingInforme) loadingInforme.style.display = 'none';
                selector.disabled = false;

                if (status === 200 && data.estado === 'ok') {
                    if (contenedorInforme) contenedorInforme.innerHTML = data.informe_ia;
                } else {
                    if (contenedorInforme) {
                        contenedorInforme.innerHTML = `
                            <div class="alert alert-warning shadow-sm mb-0">
                                <i class="bi bi-exclamation-triangle-fill me-2"></i>
                                ${data.mensaje || 'No se pudo generar el análisis solicitado.'}
                            </div>`;
                    }
                }
            })
            .catch(error => {
                console.error("Error al obtener el informe IA:", error);
                if (loadingInforme) loadingInforme.style.display = 'none';
                selector.disabled = false;
                if (contenedorInforme) {
                    contenedorInforme.innerHTML = `
                        <div class="alert alert-danger shadow-sm mb-0">
                            <i class="bi bi-x-circle-fill me-2"></i>
                            Error de conexión al generar el análisis. Inténtalo de nuevo.
                        </div>`;
                }
            });
    });

    // 2. Evento para actualizar dinámicamente la URL del botón de descarga PDF según el tipo seleccionado
    if (btnDescargarPdf) {
        btnDescargarPdf.addEventListener('click', function (evento) {
            const tipoInforme = selector.value || 'virtual';
            const url = new URL(btnDescargarPdf.href, window.location.origin);
            url.searchParams.set('informe', tipoInforme);
            btnDescargarPdf.href = url.toString();
            // No hace falta preventDefault: permitimos que el navegador siga el enlace para la descarga
        });
    }
});