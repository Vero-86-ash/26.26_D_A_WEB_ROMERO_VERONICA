/*!
* Start Bootstrap - Agency v7.0.12 (https://startbootstrap.com/theme/agency)
* Copyright 2013-2023 Start Bootstrap
* Licensed under MIT (https://github.com/StartBootstrap/startbootstrap-agency/blob/master/LICENSE)
*/

window.addEventListener('DOMContentLoaded', event => {

    // --- 1. Navbar shrink y ScrollSpy (Plantilla Agency) ---
    var navbarShrink = function () {
        const navbarCollapsible = document.body.querySelector('#mainNav');
        if (!navbarCollapsible) {
            return;
        }
        if (window.scrollY === 0) {
            navbarCollapsible.classList.remove('navbar-shrink');
        } else {
            navbarCollapsible.classList.add('navbar-shrink');
        }
    };

    navbarShrink();
    document.addEventListener('scroll', navbarShrink);

    const mainNav = document.body.querySelector('#mainNav');
    if (mainNav) {
        new bootstrap.ScrollSpy(document.body, {
            target: '#mainNav',
            rootMargin: '0px 0px -40%',
        });
    }

    const navbarToggler = document.body.querySelector('.navbar-toggler');
    const responsiveNavItems = [].slice.call(
        document.querySelectorAll('#navbarResponsive .nav-link')
    );
    responsiveNavItems.map(function (responsiveNavItem) {
        responsiveNavItem.addEventListener('click', () => {
            if (window.getComputedStyle(navbarToggler).display !== 'none') {
                navbarToggler.click();
            }
        });
    });

    // --- 2. Lógica de Registro de Usuario (Validación en tiempo real) ---
    const validarRealTime = (input, regex, msgError, msgExito) => {
        if (!input) return false;
        const errorDiv = document.getElementById(`error-${input.id}`);
        const valor = input.value.trim();
        const esValido = valor !== "" && regex.test(valor);
        
        if (valor === "") {
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

    const nombreUsuarioInput = document.getElementById('nombre-usuario');
    const emailUsuarioInput = document.getElementById('email-usuario');
    const claveUsuarioInput = document.getElementById('clave-usuario');

    if (nombreUsuarioInput) {
        nombreUsuarioInput.addEventListener('input', () => validarRealTime(nombreUsuarioInput, /^[A-ZÁÉÍÓÚÑ][a-zA-ZáéíóúñÁÉÍÓÚÑ]+(?:\s+[A-ZÁÉÍÓÚÑ][a-zA-ZáéíóúñÁÉÍÓÚÑ]+)+$/, "Debe ser: Nombre Apellido (Iniciales Mayúsculas)", "✓ Correcto"));
    }
    if (emailUsuarioInput) {
        emailUsuarioInput.addEventListener('input', () => validarRealTime(emailUsuarioInput, /^[^\s@]+@[^\s@]+\.[^\s@]+$/, "Correo inválido", "✓ Correcto"));
    }
    if (claveUsuarioInput) {
        claveUsuarioInput.addEventListener('input', () => validarRealTime(claveUsuarioInput, /^(?=.*[A-Z])(?=.*\*).+$/, "La clave debe incluir al menos una Mayúscula y un asterisco (*)", "✓ Clave segura"));
    }

    // --- 3. Lógica de Reservas y Validación del Nombre ---
    const formReserva = document.getElementById('form-reserva');
    const inputNombreReserva = document.getElementById('nombre-reserva');
    const errorNombreReserva = document.getElementById('error-nombre-reserva');
    const listaReservas = document.getElementById('lista-reservas');
    const contadorSpan = document.getElementById('contador');
    const inputFecha = document.getElementById('fecha-reserva');
    let totalReservas = 0;

    // Bloquear fechas pasadas en el calendario de reservas
    if (inputFecha) {
        inputFecha.setAttribute('min', new Date().toISOString().split('T')[0]);
    }

    // Regex estricta para el nombre de reserva: Nombre y Apellido con iniciales en mayúscula
    const regexNombreReserva = /^[A-ZÁÉÍÓÚÑ][a-zA-ZáéíóúñÁÉÍÓÚÑ]+\s+[A-ZÁÉÍÓÚÑ][a-zA-ZáéíóúñÁÉÍÓÚÑ]+$/;

    const validarNombreReservaFn = () => {
        if (!inputNombreReserva) return false;
        const valor = inputNombreReserva.value.trim();
        const esValido = regexNombreReserva.test(valor);

        if (valor === "") {
            inputNombreReserva.classList.remove('is-valid', 'is-invalid');
            if (errorNombreReserva) errorNombreReserva.textContent = "";
        } else {
            inputNombreReserva.classList.toggle('is-valid', esValido);
            inputNombreReserva.classList.toggle('is-invalid', !esValido);
            
            if (errorNombreReserva) {
                errorNombreReserva.textContent = esValido ? "✓ Correcto" : "Formato inválido (Ej: Juan Perez)";
                errorNombreReserva.style.color = esValido ? "#2ecc71" : "#ff4757";
            }
        }
        return esValido;
    };

    if (inputNombreReserva) {
        inputNombreReserva.addEventListener('input', validarNombreReservaFn);
    }

    // Manejar el envío del formulario de reservas
    if (formReserva) {
        formReserva.addEventListener('submit', (e) => {
            e.preventDefault();

            const servicioInput = document.getElementById('servicio-reserva');
            const turnoInput = document.getElementById('turno-reserva');

            const servicio = servicioInput ? servicioInput.value : "";
            const fecha = inputFecha ? inputFecha.value : "";
            const turno = turnoInput ? turnoInput.value : "";

            if (validarNombreReservaFn() && servicio && fecha && turno) {
                totalReservas++;
                if (contadorSpan) contadorSpan.textContent = totalReservas;

                const card = document.createElement('div');
                card.className = "col-md-4 mb-3";
                card.innerHTML = `
                    <div class="card shadow-sm border-success">
                        <div class="card-header bg-success text-white">Reserva #${totalReservas}</div>
                        <div class="card-body">
                            <h5 class="card-title">${inputNombreReserva.value.trim()}</h5>
                            <p class="card-text mb-1"><strong>Servicio:</strong> ${servicio}</p>
                            <p class="card-text mb-1"><strong>Día:</strong> ${fecha}</p>
                            <p class="card-text"><strong>Turno:</strong> ${turno}</p>
                            <button class="btn btn-sm btn-outline-danger mt-2" onclick="this.closest('.col-md-4').remove()">Eliminar</button>
                        </div>
                    </div>
                `;
                if (listaReservas) listaReservas.appendChild(card);
                
                formReserva.reset();
                inputNombreReserva.classList.remove('is-valid', 'is-invalid');
                if (errorNombreReserva) errorNombreReserva.textContent = "";
            } else {
                alert("Por favor, completa todos los campos correctamente.");
            }
        });
    }
});