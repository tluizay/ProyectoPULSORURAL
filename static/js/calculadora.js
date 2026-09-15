// static/js/calculadora.js
// Calculadora de productividad: margen + proyección plurianual + gráfica de sensibilidad.
let miGrafica = null; // Instancia de Chart.js, para destruirla antes de redibujar

document.addEventListener("click", async function (evento) {
    const botonCalcular = evento.target.closest("#btn-calcular");
    if (!botonCalcular) return;

    evento.preventDefault();

    const formCalculadora = document.getElementById("form-calculadora");
    if (!formCalculadora) {
        console.error("No se encuentra #form-calculadora en el DOM. ¿La sesión está iniciada?");
        return;
    }

    const urlCalcular = formCalculadora.dataset.calcularUrl;
    // URL de la gráfica: la vista 'calculadora' NO devuelve la clave 'chart',
    // esa la sirve 'grafica_comparativa'. Por eso hacen falta las dos peticiones.
    const urlGrafica = formCalculadora.dataset.graficaUrl;

    if (!urlCalcular) {
        console.error("Falta el atributo data-calcular-url en #form-calculadora.");
        return;
    }

    const divError = document.getElementById("error-calculadora");
    function mostrarError(mensaje) {
        if (!divError) return;
        divError.textContent = mensaje;
        divError.classList.remove("d-none");
    }
    function limpiarError() {
        if (!divError) return;
        divError.textContent = "";
        divError.classList.add("d-none");
    }
    limpiarError();

    const valorDe = (id) => (document.getElementById(id)?.value ?? "").trim();

    const superficie_ha = valorDe("superficie_ha");
    const rendimiento_kg_ha = valorDe("rendimiento_kg_ha");
    const precio_kg = valorDe("precio_kg");
    const coste_ha = valorDe("coste_ha");
    const anios = valorDe("anios");           // campo oculto, lo rellena la plantilla
    const tasa_interes = valorDe("tasa_interes");

    if (!superficie_ha || !rendimiento_kg_ha || !precio_kg) {
        mostrarError("Por favor, completa los campos obligatorios (Superficie, Rendimiento y Precio).");
        return;
    }

    if (Number(superficie_ha) <= 0) {
        mostrarError("La superficie debe ser mayor que 0.");
        return;
    }

    const params = new URLSearchParams({
        superficie_ha,
        rendimiento_kg_ha,
        precio_kg,
        coste_ha,
        anios,
        tasa_interes
    });

    const cabeceras = { "X-Requested-With": "XMLHttpRequest" };

    botonCalcular.disabled = true;
    const textoOriginalBoton = botonCalcular.innerHTML;
    botonCalcular.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span> Calculando...';

    try {
        // Petición 1: los números del panel de resultados
        const respuestaCalculo = await fetch(`${urlCalcular}?${params}`, { headers: cabeceras });
        const datosCalculo = await respuestaCalculo.json();

        if (!respuestaCalculo.ok) {
            throw new Error(datosCalculo.error || "Error en el cálculo.");
        }

        pintarResultados(datosCalculo);

        // Petición 2: la serie para la gráfica (base, +2 % y -2 %)
        if (urlGrafica) {
            const respuestaGrafica = await fetch(`${urlGrafica}?${params}`, { headers: cabeceras });
            const datosGrafica = await respuestaGrafica.json();

            if (respuestaGrafica.ok && datosGrafica.chart) {
                renderizarGrafica(datosGrafica.chart);
            } else {
                console.warn("No se pudo obtener la gráfica:", datosGrafica.error || respuestaGrafica.status);
            }
        } else {
            console.warn("Falta data-grafica-url en #form-calculadora; no se dibuja la gráfica.");
        }

    } catch (error) {
        console.error("Error en la petición de cálculo:", error);
        mostrarError(error.message || "No se pudo completar el cálculo.");
    } finally {
        botonCalcular.disabled = false;
        botonCalcular.innerHTML = textoOriginalBoton;
    }
});

// Formateadores con locale español, para que 1234.5 salga como 1.234,5
const formatoNumero = new Intl.NumberFormat('es-ES', { maximumFractionDigits: 2 });
const formatoEuros = new Intl.NumberFormat('es-ES', { style: 'currency', currency: 'EUR' });

function escribirEn(id, texto) {
    const nodo = document.getElementById(id);
    if (nodo) nodo.textContent = texto;
}

function pintarResultados(datos) {
    // Si vienen varios años usamos el último de la proyección; si no, el cálculo base.
    const fila = (datos.proyeccion && datos.proyeccion.length > 0)
        ? datos.proyeccion[datos.proyeccion.length - 1]
        : datos;

    if (fila.produccion_total_kg === undefined) return;

    escribirEn("res-produccion", `${formatoNumero.format(fila.produccion_total_kg)} kg`);
    escribirEn("res-ingreso", formatoEuros.format(fila.ingreso_total));
    escribirEn("res-coste", formatoEuros.format(fila.coste_total));
    escribirEn("res-margen", formatoEuros.format(fila.margen_total));
    escribirEn("res-margen-ha", `${formatoEuros.format(fila.margen_por_ha)}/ha`);
}

function renderizarGrafica(chartData) {
    const canvasElement = document.getElementById('graficaProductividad');
    if (!canvasElement) return;

    if (typeof Chart === "undefined") {
        console.error("Chart.js no está cargado. Revisa el <script> de chart.js en base.html.");
        return;
    }

    const ctx = canvasElement.getContext('2d');

    // Destruimos la gráfica anterior para evitar el solapamiento al recalcular
    if (miGrafica) {
        miGrafica.destroy();
        miGrafica = null;
    }

    miGrafica = new Chart(ctx, {
        type: 'line',
        data: chartData,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                mode: 'index',
                intersect: false
            },
            plugins: {
                legend: { position: 'top' },
                tooltip: {
                    callbacks: {
                        label: function (context) {
                            const etiqueta = context.dataset.label ? `${context.dataset.label}: ` : '';
                            if (context.parsed.y === null) return etiqueta;
                            return etiqueta + formatoEuros.format(context.parsed.y);
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: false,
                    ticks: {
                        callback: function (value) {
                            return `${formatoNumero.format(value)} €`;
                        }
                    }
                }
            }
        }
    });
}