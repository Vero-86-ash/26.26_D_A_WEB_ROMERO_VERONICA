document.addEventListener('DOMContentLoaded', () => {
    // --- 1. Lógica de Registro de Usuario ---
    const validarRealTime = (input, regex, msgError, msgExito) => {
        const errorDiv = document.getElementById(`error-${input.id}`);
        const esValido = input.value !== "" && regex.test(input.value);
        
        if (input.value === "") {
            input.classList.remove('is-valid', 'is-invalid');
            if (errorDiv) {
                errorDiv.textContent = "";
                errorDiv.classList.remove('text-success', 'text-danger');
            }
        } else {
            if (errorDiv) {
                errorDiv.textContent = esValido ? msgExito : msgError;
                errorDiv.style.color = esValido ? '#2ecc71' : '#ff4757';
                errorDiv.classList.toggle('text-success', esValido);
                errorDiv.classList.toggle('text-danger', !esValido);
            }
            input.classList.toggle('is-valid', esValido);
            input.classList.toggle('is-invalid', !esValido);
        }
        return esValido;
    };

    const nombreInput = document.getElementById('nombre-usuario');
    const emailInput = document.getElementById('email-usuario');
    const claveInput = document.getElementById('clave-usuario');

    if(nombreInput) nombreInput.addEventListener('input', () => validarRealTime(nombreInput, /^[A-ZÁÉÍÓÚÑ][a-zA-ZáéíóúñÁÉÍÓÚÑ]+(?:\s+[A-ZÁÉÍÓÚÑ][a-zA-ZáéíóúñÁÉÍÓÚÑ]+)+$/, "Debe ser: Nombre Apellido (Iniciales Mayúsculas)", "✓ Correcto"));
    if(emailInput) emailInput.addEventListener('input', () => validarRealTime(emailInput, /^[^\s@]+@[^\s@]+\.[^\s@]+$/, "Correo inválido", "✓ Correcto"));
    if(claveInput) claveInput.addEventListener('input', () => validarRealTime(claveInput, /^(?=.*[A-Z])(?=.*\*).+$/, "La clave debe incluir al menos una Mayúscula y un asterisco (*)", "✓ Clave segura"));

    // --- 2. Lógica de Reservas ---
    const formReserva = document.getElementById('form-reserva');
    const lista = document.getElementById('lista-reservas');
    const contador = document.getElementById('contador');
    let total = 0;

    const aplicarEstilo = (input, esValido) => {
        input.classList.toggle('is-valid', esValido);
        input.classList.toggle('is-invalid', !esValido && input.value !== "");
    };

    const inputNombreReserva = document.getElementById('nombre');
    const inputDescripcion = document.getElementById('descripcion');
    const inputCategoria = document.getElementById('categoria');

    if (inputNombreReserva) inputNombreReserva.addEventListener('input', () => aplicarEstilo(inputNombreReserva, inputNombreReserva.value.trim().length >= 3));
    if (inputDescripcion) inputDescripcion.addEventListener('input', () => aplicarEstilo(inputDescripcion, inputDescripcion.value.trim() !== ""));
    if (inputCategoria) inputCategoria.addEventListener('input', () => aplicarEstilo(inputCategoria, inputCategoria.value !== ""));

    if (formReserva) {
        formReserva.addEventListener('submit', (e) => {
            e.preventDefault();
            const v1 = inputNombreReserva.value.trim().length >= 3;
            const v2 = inputDescripcion.value.trim() !== "";
            const v3 = inputCategoria.value !== "";

            if (v1 && v2 && v3) {
                total++;
                if (contador) contador.textContent = total;

                const colDiv = document.createElement('div');
                colDiv.className = "col-md-6 col-lg-4";
                colDiv.innerHTML = `
                    <div class="p-3 text-white mb-2" style="background-color: #111; border: 1px solid #333; border-left: 5px solid #ff6600; border-radius: 8px;">
                        <div class="d-flex justify-content-between align-items-start mb-2">
                            <h5 class="text-warning mb-0">${inputNombreReserva.value.trim()}</h5>
                            <span class="badge bg-info text-dark">${inputCategoria.value}</span>
                        </div>
                        <p class="small text-white-50">${inputDescripcion.value.trim()}</p>
                    </div>
                `;
                if (lista) lista.appendChild(colDiv);
                formReserva.reset();
                [inputNombreReserva, inputDescripcion, inputCategoria].forEach(c => { if (c) c.classList.remove('is-valid'); });
            } else {
                alert("Por favor, completa los campos correctamente.");
            }
        });
    }
});
document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('form-reserva');
    const inputNombre = document.getElementById('nombre-reserva');
    const errorNombre = document.getElementById('error-nombre-reserva');
    const lista = document.getElementById('lista-reservas');
    const contadorSpan = document.getElementById('contador');
    const inputFecha = document.getElementById('fecha-reserva');
    let total = 0;

    // Bloquear fechas pasadas
    if (inputFecha) {
        inputFecha.setAttribute('min', new Date().toISOString().split('T')[0]);
    }

    // Regex: Nombre y Apellido con Mayúsculas iniciales
    const regexNombre = /^[A-ZÁÉÍÓÚÑ][a-zA-ZáéíóúñÁÉÍÓÚÑ]+\s+[A-ZÁÉÍÓÚÑ][a-zA-ZáéíóúñÁÉÍÓÚÑ]+$/;

    const validarNombre = () => {
        const esValido = regexNombre.test(inputNombre.value.trim());
        inputNombre.classList.toggle('is-valid', esValido);
        inputNombre.classList.toggle('is-invalid', !esValido && inputNombre.value !== "");
        
        if (inputNombre.value === "") {
            errorNombre.textContent = "";
        } else {
            errorNombre.textContent = esValido ? "✓ Correcto" : "Formato inválido (Ej: Juan Perez)";
            errorNombre.style.color = esValido ? "#2ecc71" : "#ff4757";
        }
        return esValido;
    };

    if (inputNombre) {
        inputNombre.addEventListener('input', validarNombre);
    }

    if (form) {
        form.addEventListener('submit', (e) => {
            e.preventDefault();

            const servicio = document.getElementById('servicio-reserva').value;
            const fecha = inputFecha.value;
            const turno = document.getElementById('turno-reserva').value;

            if (validarNombre() && servicio && fecha && turno) {
                total++;
                contadorSpan.textContent = total;

                const card = document.createElement('div');
                card.className = "col-md-4 mb-3";
                card.innerHTML = `
                    <div class="card shadow-sm border-success">
                        <div class="card-header bg-success text-white">Reserva #${total}</div>
                        <div class="card-body">
                            <h5 class="card-title">${inputNombre.value}</h5>
                            <p class="card-text mb-1"><strong>Servicio:</strong> ${servicio}</p>
                            <p class="card-text mb-1"><strong>Día:</strong> ${fecha}</p>
                            <p class="card-text"><strong>Turno:</strong> ${turno}</p>
                            <button class="btn btn-sm btn-outline-danger mt-2" onclick="this.closest('.col-md-4').remove()">Eliminar</button>
                        </div>
                    </div>
                `;
                lista.appendChild(card);
                form.reset();
                inputNombre.classList.remove('is-valid');
                errorNombre.textContent = "";
            } else {
                alert("Por favor, completa todos los campos correctamente.");
            }
        });
    }
});