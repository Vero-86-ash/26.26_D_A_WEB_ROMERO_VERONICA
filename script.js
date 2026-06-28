document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('form-servicio');
    const listaServicios = document.getElementById('lista-servicios-dinamicos');
    const contadorTexto = document.getElementById('total-servicios');
    const feedback = document.getElementById('feedback-formulario');

    let total = 0;

    form.addEventListener('submit', (e) => {
        e.preventDefault();

        const nombre = document.getElementById('servicio-nombre').value.trim();
        const categoria = document.getElementById('servicio-categoria').value;
        const desc = document.getElementById('servicio-descripcion').value.trim();

        if (nombre === "" || categoria === "" || desc === "") {
            feedback.textContent = "Por favor, completa todos los campos.";
            feedback.className = "alert alert-danger mt-3";
            feedback.classList.remove('d-none');
            return;
        }

        feedback.classList.add('d-none');
        
        const col = document.createElement('div');
        col.className = "col-md-4";
        
        col.innerHTML = `
            <div class="card bg-dark text-white border-warning h-100 shadow">
                <div class="card-body">
                    <h5 class="card-title text-warning">${nombre}</h5>
                    <h6 class="card-subtitle mb-2 text-info">${categoria}</h6>
                    <p class="card-text">${desc}</p>
                    <button class="btn btn-outline-danger btn-sm btn-eliminar">Eliminar</button>
                </div>
            </div>
        `;

        const btnEliminar = col.querySelector('.btn-eliminar');
        btnEliminar.addEventListener('click', () => {
            col.remove();
            total--;
            actualizarContador();
        });

        listaServicios.appendChild(col);

        total++;
        actualizarContador();

        form.reset();
    });

    function actualizarContador() {
        contadorTexto.textContent = `Total de registros creados: ${total}`;
    }
});