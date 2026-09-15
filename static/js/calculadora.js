// C. Calculadora con diagnóstico, delegación global robusta y soporte plurianual / gráfica
let miGrafica = null; // Variable global para destruir la gráfica anterior si se recalcula

document.addEventListener("click", async function (evento) {
    const botonCalcular = evento.target.closest("#btn-calcular");
    if (!botonCalcular) return; // Si no se hizo clic en el botón de calcular, ignorar.

    evento.preventDefault();
    console.log("¡Clic detectado en #btn-calcular!");

    const formCalculadora = document.getElementById("form-calculadora");
    if (!formCalculadora) {
        console.error("Error crítico: No se encuentra el elemento #form-calculadora en el DOM. ¿Estás logueado?");
        alert("Debes iniciar sesión para usar la calculadora.");
        return;
    }

    const urlCalcular = formCalculadora.dataset.calcularUrl || formCalculadora.getAttribute('data-calcular-url');
    if (!urlCalcular) {
        console.error("Error: El formulario no tiene el atributo data-calcular-url.");
        return;
    }

    const divError = document.getElementById("error-calculadora");
    if (divError) {
        divError.classList.add("d-none");
        divError.textContent = "";
    }

    // Recoger valores del formulario (incluyendo los nuevos campos de años y tasa de interés)
    const superficie_ha = document.getElementById("superficie_ha")?.value || "";
    const rendimiento_kg_ha = document.getElementById("rendimiento_kg_ha")?.value || "";
    const precio_kg = document.getElementById("precio_kg")?.value || "";
    const coste_ha = document.getElementById("coste_ha")?.value || "";
    const anios = document.getElementById("anios")?.value || "";
    const tasa_interes = document.getElementById("tasa_interes")?.value || "";

    // Validación rápida en cliente para campos obligatorios
    if (!superficie_ha || !rendimiento_kg_ha || !precio_kg) {
        if (divError) {
            divError.textContent = "Por favor, completa los campos obligatorios (Superficie, Rendimiento y Precio).";
            divError.classList.remove("d-none");
        }
        return;
    }

    // Construir parámetros GET de forma limpia con URLSearchParams
    const params = new URLSearchParams({
        superficie_ha,
        rendimiento_kg_ha,
        precio_kg,
        coste_ha,
        anios,
        tasa_interes
    });

    const url = `${urlCalcular}?${params.toString()}`;
    console.log("Enviando petición a la URL:", url);

    try {
        const response = await fetch(url, {
            method: "GET",
            headers: { "X-Requested-With": "XMLHttpRequest" }
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || "Error en el cálculo.");
        }

        console.log("Datos de cálculo recibidos:", data);

        // 1. Rellenar la tarjeta de resultados con el último año de la proyección (o el base)
        if (data.proyeccion && data.proyeccion.length > 0) {
            const ultimoAnio = data.proyeccion[data.proyeccion.length - 1];
            
            if (document.getElementById("res-produccion")) document.getElementById("res-produccion").textContent = `${Number(ultimoAnio.produccion_total_kg).toLocaleString()} kg`;
            if (document.getElementById("res-ingreso")) document.getElementById("res-ingreso").textContent = `${Number(ultimoAnio.ingreso_total).toLocaleString()} €`;
            if (document.getElementById("res-coste")) document.getElementById("res-coste").textContent = `${Number(ultimoAnio.coste_total).toLocaleString()} €`;
            if (document.getElementById("res-margen")) document.getElementById("res-margen").textContent = `${Number(ultimoAnio.margen_total).toLocaleString()} €`;
            if (document.getElementById("res-margen-ha")) document.getElementById("res-margen-ha").textContent = `${Number(ultimoAnio.margen_por_ha).toLocaleString()} €/ha`;
        }

        // 2. Pintar o actualizar la Gráfica con Chart.js si viene en la respuesta
        if (data.chart) {
            renderizarGrafica(data.chart);
        }

    } catch (error) {
        console.error("Error en la petición de cálculo:", error);
        if (divError) {
            divError.textContent = error.message;
            divError.classList.remove("d-none");
        }
    }
});

function renderizarGrafica(chartData) {
    const canvasElement = document.getElementById('graficaProductividad');
    if (!canvasElement) return;

    const ctx = canvasElement.getContext('2d');

    // Si ya existe una gráfica previa, la destruimos para evitar errores de solapamiento al recalcular
    if (miGrafica) {
        miGrafica.destroy();
    }

    miGrafica = new Chart(ctx, {
        type: 'line',
        data: chartData,
        options: {
            responsive: true,
            interaction: {
                mode: 'index',
                intersect: false,
            },
            plugins: {
                legend: {
                    position: 'top',
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            let label = context.dataset.label || '';
                            if (label) {
                                label += ': ';
                            }
                            if (context.parsed.y !== null) {
                                label += new Intl.NumberFormat('es-ES', { style: 'currency', currency: 'EUR' }).format(context.parsed.y);
                            }
                            return label;
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: false,
                    ticks: {
                        callback: function(value) {
                            return value.toLocaleString() + ' €';
                        }
                    }
                }
            }
        }
    });
}