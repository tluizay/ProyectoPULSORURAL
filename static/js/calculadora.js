
// C. Calculadora con diagnóstico y delegación global robusta
document.addEventListener("click", function (evento) {
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

    const superficie = document.getElementById("superficie_ha")?.value || "";
    const rendimiento = document.getElementById("rendimiento_kg_ha")?.value || "";
    const precio = document.getElementById("precio_kg")?.value || "";
    const coste = document.getElementById("coste_ha")?.value || "";

    // Validación rápida en cliente para campos obligatorios
    const divError = document.getElementById("error-calculadora");
    if (!superficie || !rendimiento || !precio) {
        if (divError) {
            divError.textContent = "Por favor, completa los campos obligatorios (Superficie, Rendimiento y Precio).";
            divError.classList.remove("d-none");
        }
        return;
    }

    if (divError) divError.classList.add("d-none");

    const url = `${urlCalcular}?superficie_ha=${encodeURIComponent(superficie)}&rendimiento_kg_ha=${encodeURIComponent(rendimiento)}&precio_kg=${encodeURIComponent(precio)}&coste_ha=${encodeURIComponent(coste)}`;
    
    console.log("Enviando petición a la URL:", url);

    fetch(url, {
        method: "GET",
        headers: { "X-Requested-With": "XMLHttpRequest" }
    })
    .then(response => {
        if (!response.ok) {
            return response.json().then(errData => { throw new Error(errData.error || "Error en el cálculo."); });
        }
        return response.json();
    })
    .then(data => {
        console.log("Datos de cálculo recibidos:", data);
        if(document.getElementById("res-produccion")) document.getElementById("res-produccion").textContent = `${Number(data.produccion_total_kg).toLocaleString()} kg`;
        if(document.getElementById("res-ingreso")) document.getElementById("res-ingreso").textContent = `${Number(data.ingreso_total).toLocaleString()} €`;
        if(document.getElementById("res-coste")) document.getElementById("res-coste").textContent = `${Number(data.coste_total).toLocaleString()} €`;
        if(document.getElementById("res-margen")) document.getElementById("res-margen").textContent = `${Number(data.margen_total).toLocaleString()} €`;
        if(document.getElementById("res-margen-ha")) document.getElementById("res-margen-ha").textContent = `${Number(data.margen_por_ha).toLocaleString()} €/ha`;
    })
    .catch(error => {
        console.error("Error en la petición de cálculo:", error);
        if (divError) {
            divError.textContent = error.message;
            divError.classList.remove("d-none");
        }
    });
});
