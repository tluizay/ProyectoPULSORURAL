document.addEventListener("DOMContentLoaded", function () {
    // 1. Objeto global para almacenar los datos que llegan de las APIs
    let datosPantallaActual = {
        lat: typeof lat !== 'undefined' ? lat : '',
        lon: typeof lon !== 'undefined' ? lon : '',
        datos_recinto: {},     // Se llenará con los datos del recinto si los tienes a mano
        clima_aemet: {},       // Se llenará cuando responda el fetch de AEMET
        datos_hidricos: {},    // Se llenará cuando responda el fetch de SoilGrids
        datos_suelo: {}        // Se llenará cuando responda el fetch de ITACYL
    };

    // (Opcional) Si tienes los datos del recinto en un nodo del DOM, puedes capturarlos aquí:
    const nodoRecinto = document.getElementById('recinto-data'); 
    if (nodoRecinto) {
        try {
            datosPantallaActual.datos_recinto = JSON.parse(nodoRecinto.textContent);
        } catch (e) {
            console.error("Error al leer datos del recinto:", e);
        }
    }

    // ----------------------------------------------------
    // 2. ATRAPAR LOS DATOS EN LOS FETCH EXISTENTES
    // ----------------------------------------------------
    // Asegúrate de guardar la respuesta 'data' de cada fetch en tu objeto global:

    // A. En tu fetch de AEMET:
    /*
    fetch(`/aemet/consulta_clima/?lat=${lat}&lon=${lon}`)
        .then(response => response.json())
        .then(data => {
            datosPantallaActual.clima_aemet = data; // <--- GUARDAMOS AQUÍ
            // ... resto de tu código para pintar AEMET ...
        });
    */

    // B. En tu fetch de SoilGrids:
    /*
    fetch(`${config.urlAguas}?lat=${lat}&lon=${lon}`)
        .then(response => response.json())
        .then(data => {
            datosPantallaActual.datos_hidricos = data; // <--- GUARDAMOS AQUÍ
            // ... resto de tu código para pintar Hídricos ...
        });
    */

    // C. En tu fetch de ITACYL:
    /*
    fetch(`${config.urlSuelos}?lat=${lat}&lon=${lon}`)
        .then(response => response.json())
        .then(data => {
            datosPantallaActual.datos_suelo = data; // <--- GUARDAMOS AQUÍ
            // ... resto de tu código para pintar Suelos ...
        });
    */

    // ----------------------------------------------------
    // 3. GESTIONAR EL CLIC DEL BOTÓN DE DESCARGA PDF
    // ----------------------------------------------------
    const btnPdf = document.getElementById('btn-descargar-pdf');
    if (btnPdf) {
        btnPdf.addEventListener('click', function (e) {
            e.preventDefault();

            // Cambiar aspecto del botón para mostrar que está cargando
            const textoOriginal = btnPdf.innerHTML;
            btnPdf.innerHTML = `<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Generando PDF...`;
            btnPdf.disabled = true;

            // Obtener el token CSRF de Django de forma segura
            const csrfTokenElement = document.querySelector('[name=csrfmiddlewaretoken]');
            const csrfToken = csrfTokenElement ? csrfTokenElement.value : '';

            // Enviar los datos por POST a la vista de Django
            // Antes de la línea de fetch(...):
            fetch("/sigpac/descargar_pdf_parcela/", { 
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify(datosPantallaActual)
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error("Error en el servidor al generar el PDF.");
                }
                return response.blob(); // Convertir la respuesta binaria en un archivo Blob
            })
            .then(blob => {
                // Crear un enlace temporal en el navegador para forzar la descarga del PDF
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = "Informe_Completo_Parcela.pdf";
                document.body.appendChild(a);
                a.click();
                a.remove();
                window.URL.revokeObjectURL(url);
            })
            .catch(error => {
                console.error("Error al descargar el PDF:", error);
                alert("Hubo un problema al generar el PDF. Inténtalo de nuevo.");
            })
            .finally(() => {
                // Restaurar el botón a su estado original
                btnPdf.innerHTML = textoOriginal;
                btnPdf.disabled = false;
            });
        });
    }
});