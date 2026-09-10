
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