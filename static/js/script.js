// URL base de la API backend
const BASE_URL = "https://okijulian.pythonanywhere.com";
// --- FUNCIONES DE UTILIDAD ---

/**
 * Muestra un mensaje temporal en la pantalla.
 * @param {string} texto - El texto a mostrar.
 * @param {string} tipo - El tipo de mensaje ('success' o 'error').
 */
function mostrarMensaje(texto, tipo) {
    const mensajeDiv = document.getElementById('mensaje');
    if (mensajeDiv) {
        mensajeDiv.textContent = texto;
        // Asigna una clase CSS para estilizar el mensaje como éxito o error
        mensajeDiv.className = tipo;
    }
}

// --- FUNCIONES DE AUTENTICACIÓN ---

/**
 * Registra un nuevo usuario.
 */
async function registrar() {
    const usuario = document.getElementById('reg-usuario').value;
    const contrasena = document.getElementById('reg-contrasena').value;
    const pregunta = document.getElementById('reg-pregunta').value;
    const respuesta = document.getElementById('reg-respuesta').value;

    try {
        const response = await fetch(`${BASE_URL}/registro`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ usuario, contrasena, pregunta, respuesta })
        });
        const data = await response.json();
        if (response.ok) {
            mostrarMensaje('Registro exitoso. Serás redirigido al login.', 'success');
            window.location.href = 'login.html';
        } else {
            mostrarMensaje(data.message || 'Error en el registro.', 'error');
        }
    } catch (error) {
        mostrarMensaje('Error de conexión con el servidor.', 'error');
    }
}

/**
 * Inicia sesión de un usuario.
 */
async function iniciarSesion() {
    const usuario = document.getElementById('login-usuario').value;
    const contrasena = document.getElementById('login-contrasena').value;

    try {
        const response = await fetch(`${BASE_URL}/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ usuario, contrasena })
        });
        const data = await response.json();
        if (response.ok) {
            // Guarda el token en el almacenamiento local para futuras peticiones
            localStorage.setItem('token', data.token);
            window.location.href = 'tareas.html';
        } else {
            localStorage.removeItem('token');
            mostrarMensaje(data.message || 'Error en el login.', 'error');
        }
    } catch (error) {
        mostrarMensaje('Error de conexión con el servidor.', 'error');
    }
}

/**
 * Cierra la sesión del usuario.
 */
function cerrarSesion() {
    localStorage.removeItem('token');
    window.location.href = 'index.html';
}

/**
 * Verifica si el usuario está logueado. Si no, lo redirige al login.
 */
function verificarEstadoSesion() {
    const token = localStorage.getItem('token');
    // Si no hay token y el usuario está en la página de tareas, redirigir a login
    if (!token && window.location.pathname.endsWith('tareas.html')) {
        window.location.href = 'login.html';
    }
}

// --- FUNCIONES DE RECUPERACIÓN DE CONTRASEÑA ---

/**
 * Obtiene la pregunta de seguridad del usuario.
 */
async function obtenerPreguntaSeguridad() {
    const usuario = document.getElementById('rec-usuario').value;
    try {
        const response = await fetch(`${BASE_URL}/recuperar/preguntas`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ usuario })
        });
        const data = await response.json();
        if (response.ok) {
            document.getElementById('pregunta-seguridad').textContent = data.pregunta;
            // Oculta el primer paso y muestra el segundo
            document.getElementById('step1').style.display = 'none';
            document.getElementById('step2').style.display = 'block';
        } else {
            mostrarMensaje(data.message || 'Error al obtener la pregunta.', 'error');
        }
    } catch (error) {
        mostrarMensaje('Error de conexión con el servidor.', 'error');
    }
}

/**
 * Valida la respuesta de seguridad y actualiza la contraseña.
 */
async function validarRespuestaSeguridad() {
    const usuario = document.getElementById('rec-usuario').value;
    const respuesta = document.getElementById('rec-respuesta').value;
    const nueva_contrasena = document.getElementById('rec-nueva-contrasena').value;

    try {
        const response = await fetch(`${BASE_URL}/recuperar/validar`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ usuario, respuesta, nueva_contrasena })
        });
        const data = await response.json();
        if (response.ok) {
            mostrarMensaje('Contraseña actualizada. Serás redirigido al login.', 'success');
            setTimeout(() => { window.location.href = 'login.html'; }, 2000);
        } else {
            mostrarMensaje(data.message || 'Error al validar la respuesta.', 'error');
        }
    } catch (error) {
        mostrarMensaje('Error de conexión con el servidor.', 'error');
    }
}

// --- FUNCIONES DE GESTIÓN DE TAREAS (CRUD) ---

/**
 * Obtiene y muestra la lista de tareas del usuario.
 */
async function obtenerTareas() {
    const token = localStorage.getItem('token');
    if (!token) return;

    try {
        const response = await fetch(`${BASE_URL}/tareas`, {
            method: 'GET',
            headers: { 'Authorization': `Bearer ${token}` }
        });

        if (response.ok) {
            const tareas = await response.json();
            const listaTareas = document.getElementById('lista-tareas');
            listaTareas.innerHTML = ''; // Limpiar la lista antes de añadir nuevos elementos

            tareas.forEach(tarea => {
                const li = document.createElement('li');
                li.className = tarea.completada ? 'completada' : '';

                // Contenedor para el checkbox personalizado
                const checkboxLabel = document.createElement('label');
                checkboxLabel.className = 'task-checkbox';

                const checkboxInput = document.createElement('input');
                checkboxInput.type = 'checkbox';
                checkboxInput.checked = tarea.completada;
                checkboxInput.onchange = () => actualizarTarea(tarea.id, { completada: checkboxInput.checked });

                const checkmarkSpan = document.createElement('span');
                checkmarkSpan.className = 'checkmark';

                checkboxLabel.appendChild(checkboxInput);
                checkboxLabel.appendChild(checkmarkSpan);

                // Contenido de la tarea
                const contenidoTarea = document.createElement('span');
                contenidoTarea.className = 'task-content';
                contenidoTarea.textContent = tarea.contenido;

                // Botones de acciones
                const accionesTarea = document.createElement('div');
                accionesTarea.className = 'task-actions';
                
                const botonCompletar = document.createElement('button');
                botonCompletar.className = 'complete-btn';
                botonCompletar.textContent = tarea.completada ? 'Desmarcar' : 'Completar';
                botonCompletar.onclick = () => actualizarTarea(tarea.id, { completada: !tarea.completada });
                
                const botonEliminar = document.createElement('button');
                botonEliminar.className = 'delete-btn';
                botonEliminar.textContent = 'Eliminar';
                botonEliminar.onclick = () => eliminarTarea(tarea.id);

                accionesTarea.appendChild(botonCompletar);
                accionesTarea.appendChild(botonEliminar);

                // Ensamblar todo en el elemento de la lista
                li.appendChild(checkboxLabel);
                li.appendChild(contenidoTarea);
                li.appendChild(accionesTarea);
                
                listaTareas.appendChild(li);
            });
        } else {
            // Si la respuesta no es OK (ej. token expirado), cerrar sesión
            cerrarSesion();
        }
    } catch (error) {
        mostrarMensaje('Error de conexión con el servidor.', 'error');
    }
}

/**
 * Crea una nueva tarea.
 */
async function crearTarea() {
    const token = localStorage.getItem('token');
    const contenido = document.getElementById('nueva-tarea').value;
    if (!contenido) {
        mostrarMensaje('El contenido de la tarea no puede estar vacío.', 'error');
        return;
    }

    try {
        const response = await fetch(`${BASE_URL}/tareas`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({ contenido })
        });
        if (response.ok) {
            document.getElementById('nueva-tarea').value = ''; // Limpiar el input
            obtenerTareas(); // Refrescar la lista de tareas
        } else {
            mostrarMensaje('Error al crear la tarea.', 'error');
        }
    } catch (error) {
        mostrarMensaje('Error de conexión con el servidor.', 'error');
    }
}

/**
 * Actualiza una tarea existente (marcar como completada o cambiar contenido).
 * @param {number} id - El ID de la tarea a actualizar.
 * @param {object} datosParaActualizar - Los datos a actualizar (ej. { completada: true }).
 */
async function actualizarTarea(id, datosParaActualizar) { 
    const token = localStorage.getItem('token');
    try {
        const response = await fetch(`${BASE_URL}/tareas/${id}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify(datosParaActualizar)
        });
        if (response.ok) {
            obtenerTareas(); // Refrescar la lista de tareas
        } else {
            mostrarMensaje('Error al actualizar la tarea.', 'error');
        }
    } catch (error) {
        mostrarMensaje('Error de conexión con el servidor.', 'error');
    }
}

/**
 * Elimina una tarea.
 * @param {number} id - El ID de la tarea a eliminar.
 */
async function eliminarTarea(id) {
    const token = localStorage.getItem('token');
    // Pedir confirmación antes de eliminar
    if (!confirm('¿Estás seguro de que quieres eliminar esta tarea?')) return;

    try {
        const response = await fetch(`${BASE_URL}/tareas/${id}`, {
            method: 'DELETE',
            headers: { 'Authorization': `Bearer ${token}` }
        });
        if (response.ok) {
            obtenerTareas(); // Refrescar la lista de tareas
        } else {
            mostrarMensaje('Error al eliminar la tarea.', 'error');
        }
    } catch (error) {
        mostrarMensaje('Error de conexión con el servidor.', 'error');
    }
}
