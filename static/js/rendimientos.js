(function () {
    function iniciarGraficas() {
        const loadingIndicator = document.getElementById('loadingIndicator');
        const chartsContainer = document.getElementById('chartsContainer');

        try {
            const elPanel = document.getElementById('json-datos-panel');
            if (!elPanel || !elPanel.textContent.trim()) {
                console.warn("No se encontró el elemento #json-datos-panel o está vacío.");
                return;
            }

            const data = JSON.parse(elPanel.textContent);
            
            // 1. Gráfica Vegetal
            const canvasVegetal = document.getElementById('graficoVegetal');
            if (canvasVegetal && data.vegetal) {
                new Chart(canvasVegetal.getContext('2d'), {
                    type: 'bar',
                    data: data.vegetal,
                    options: { responsive: true, maintainAspectRatio: false }
                });
            }

            // 2. Gráfica Animal
            const canvasAnimal = document.getElementById('graficoAnimal');
            if (canvasAnimal && data.animal) {
                new Chart(canvasAnimal.getContext('2d'), {
                    type: 'bar',
                    data: data.animal,
                    options: { responsive: true, maintainAspectRatio: false }
                });
            }

            // 3. Gráfica de Líneas (Evolución Global)
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

            // 4. Gráfica Circular (Distribución)
            const canvasProvincial = document.getElementById('chartProvincialAnio');
            if (canvasProvincial && data.provincial_anio) {
                new Chart(canvasProvincial.getContext('2d'), {
                    type: 'pie',
                    data: data.provincial_anio,
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: { legend: { position: 'right' } }
                    }
                });
            }

            // Ocultar spinner y mostrar contenedor
            if (loadingIndicator) loadingIndicator.style.display = 'none';
            if (chartsContainer) chartsContainer.style.display = 'block';

        } catch (error) {
            console.error("Error crítico al renderizar las gráficas:", error);
            if (loadingIndicator) {
                loadingIndicator.innerHTML = `
                    <div class="alert alert-danger shadow-sm">
                        <i class="bi bi-exclamation-triangle-fill me-2"></i> Error al procesar las gráficas: ${error.message}
                    </div>`;
            }
        }
    }

    // Ejecutar inmediatamente si el DOM ya cargó, o esperar al evento
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', iniciarGraficas);
    } else {
        iniciarGraficas();
    }
})();