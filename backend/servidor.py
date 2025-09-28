# -*- coding: utf-8 -*-
# Importaciones necesarias para el funcionamiento del servidor
from flask import Flask, request, jsonify
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
from functools import wraps
from flask_cors import CORS

# --- CONFIGURACIÓN INICIAL ---

# Inicialización de la aplicación Flask
app = Flask(__name__)
# Habilitar CORS para permitir peticiones desde el frontend
# Permitir peticiones solo desde tu página de GitHub Pages
CORS(app, resources={r"/*": {"origins": "https://okijulian.github.io"}})
# Clave secreta para la firma de tokens JWT (en un entorno de producción, esto debería ser más seguro y no estar en el código)
app.config['SECRET_KEY'] = 'tu_super_secreto'

# Nombre del archivo de la base de datos
NOMBRE_BD = "tasks.db"

# --- DECORADOR DE AUTENTICACIÓN ---

def token_requerido(f):
    """
    Decorador que verifica la validez de un token JWT en la cabecera 'Authorization'.
    Si el token es válido, obtiene los datos del usuario y los pasa a la ruta protegida.
    Si no, devuelve un error 401.
    """
    @wraps(f)
    def decorador(*args, **kwargs):
        token = None
        # El token se espera en el formato 'Bearer <token>'
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(" ")[1]

        if not token:
            # No se proporcionó token
            return jsonify({'message': '¡El token es requerido!'}), 401

        try:
            # Decodificar el token para obtener los datos (payload)
            datos = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            # Buscar al usuario en la base de datos usando el nombre de usuario del token
            with sqlite3.connect(NOMBRE_BD) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM usuarios WHERE usuario = ?", (datos['usuario'],))
                usuario_actual = cursor.fetchone()
        except Exception as e:
            # El token es inválido (expirado, malformado, etc.)
            return jsonify({'message': '¡El token es inválido!', 'error': str(e)}), 401

        # Pasa el usuario encontrado a la función de la ruta
        return f(usuario_actual, *args, **kwargs)

    return decorador

# --- INICIALIZACIÓN DE LA BASE DE DATOS ---

def inicializar_bd():
    """Crea las tablas 'usuarios' y 'tareas' si no existen."""
    with sqlite3.connect(NOMBRE_BD) as conn:
        cursor = conn.cursor()
        # Tabla para almacenar los datos de los usuarios
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario TEXT UNIQUE NOT NULL,
                contrasena TEXT NOT NULL,
                pregunta TEXT NOT NULL,
                respuesta TEXT NOT NULL
            )
        """)
        # Tabla para almacenar las tareas, con una clave foránea al usuario propietario
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tareas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                contenido TEXT NOT NULL,
                completada BOOLEAN NOT NULL CHECK (completada IN (0, 1)),
                id_usuario INTEGER NOT NULL,
                FOREIGN KEY (id_usuario) REFERENCES usuarios (id)
            )
        """)
        conn.commit()

# --- RUTAS DE AUTENTICACIÓN ---

@app.route('/registro', methods=['POST'])
def registro():
    """Registra un nuevo usuario en la base de datos."""
    datos = request.get_json()
    usuario = datos.get('usuario')
    contrasena = datos.get('contrasena')
    pregunta = datos.get('pregunta')
    respuesta = datos.get('respuesta')

    # Validar que todos los campos necesarios están presentes
    if not all([usuario, contrasena, pregunta, respuesta]):
        return jsonify({'message': 'Todos los campos (usuario, contraseña, pregunta y respuesta) son requeridos'}), 400

    # Hashear la contraseña antes de guardarla por seguridad
    contrasena_hasheada = generate_password_hash(contrasena)

    with sqlite3.connect(NOMBRE_BD) as conn:
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO usuarios (usuario, contrasena, pregunta, respuesta) VALUES (?, ?, ?, ?)",
                (usuario, contrasena_hasheada, pregunta, respuesta)
            )
            conn.commit()
            return jsonify({'message': 'Usuario registrado exitosamente'}), 201
        except sqlite3.IntegrityError:
            # Esto ocurre si el usuario ya existe (por la restricción UNIQUE)
            return jsonify({'message': 'El usuario ya existe'}), 400

@app.route('/login', methods=['POST'])
def login():
    """Inicia sesión y devuelve un token JWT si las credenciales son correctas."""
    datos = request.get_json()
    usuario = datos.get('usuario')
    contrasena = datos.get('contrasena')

    if not usuario or not contrasena:
        return jsonify({'message': 'Usuario y contraseña son requeridos'}), 400

    with sqlite3.connect(NOMBRE_BD) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT contrasena FROM usuarios WHERE usuario = ?", (usuario,))
        fila_usuario = cursor.fetchone()

        # Verificar que el usuario existe y la contraseña es correcta
        if fila_usuario and check_password_hash(fila_usuario[0], contrasena):
            # Crear el token con el nombre de usuario y una fecha de expiración
            token = jwt.encode({
                'usuario': usuario,
                'exp' : datetime.datetime.utcnow() + datetime.timedelta(minutes=30) # Expira en 30 mins
            }, app.config['SECRET_KEY'], algorithm="HS256")
            # NOTA: La clave 'token' en el JSON es usada por el frontend.
            return jsonify({'token' : token}), 200
        else:
            return jsonify({'message': 'Credenciales inválidas'}), 401

# --- RUTAS DE RECUPERACIÓN DE CONTRASEÑA ---

@app.route('/recuperar/preguntas', methods=['POST'])
def obtener_pregunta_seguridad():
    """Obtiene la pregunta de seguridad para un usuario específico."""
    datos = request.get_json()
    usuario = datos.get('usuario')
    if not usuario:
        return jsonify({'message': 'El nombre de usuario es requerido'}), 400

    with sqlite3.connect(NOMBRE_BD) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT pregunta FROM usuarios WHERE usuario = ?", (usuario,))
        fila_pregunta = cursor.fetchone()

    if fila_pregunta:
        # NOTA: La clave 'pregunta' en el JSON es usada por el frontend.
        return jsonify({'pregunta': fila_pregunta[0]}), 200
    else:
        return jsonify({'message': 'Usuario no encontrado'}), 404

@app.route('/recuperar/validar', methods=['POST'])
def validar_respuesta_seguridad():
    """Valida la respuesta de seguridad y actualiza la contraseña si es correcta."""
    datos = request.get_json()
    usuario = datos.get('usuario')
    respuesta = datos.get('respuesta')
    nueva_contrasena = datos.get('nueva_contrasena')

    if not all([usuario, respuesta, nueva_contrasena]):
        return jsonify({'message': 'Usuario, respuesta y nueva contraseña son requeridos'}), 400

    with sqlite3.connect(NOMBRE_BD) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT respuesta FROM usuarios WHERE usuario = ?", (usuario,))
        fila_respuesta = cursor.fetchone()

    if not fila_respuesta:
        return jsonify({'message': 'Usuario no encontrado'}), 404

    # Comprobar si la respuesta proporcionada coincide con la almacenada
    if fila_respuesta[0] == respuesta:
        nueva_contrasena_hasheada = generate_password_hash(nueva_contrasena)
        with sqlite3.connect(NOMBRE_BD) as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE usuarios SET contrasena = ? WHERE usuario = ?", (nueva_contrasena_hasheada, usuario))
            conn.commit()
        return jsonify({'message': 'Contraseña actualizada exitosamente'}), 200
    else:
        return jsonify({'message': 'La respuesta de seguridad es incorrecta'}), 401

# --- RUTAS DE TAREAS (CRUD) ---

@app.route('/tareas', methods=['GET'])
@token_requerido
def obtener_tareas(usuario_actual):
    """Obtiene todas las tareas del usuario que está autenticado."""
    with sqlite3.connect(NOMBRE_BD) as conn:
        cursor = conn.cursor()
        # Seleccionar solo las tareas que pertenecen al id del usuario del token
        cursor.execute("SELECT id, contenido, completada FROM tareas WHERE id_usuario = ?", (usuario_actual[0],))
        tareas = cursor.fetchall()
    
    lista_tareas = []
    for tarea in tareas:
        # NOTA: Las claves (id, contenido, completada) son usadas por el frontend.
        lista_tareas.append({'id': tarea[0], 'contenido': tarea[1], 'completada': bool(tarea[2])})
        
    return jsonify(lista_tareas), 200

@app.route('/tareas', methods=['POST'])
@token_requerido
def crear_tarea(usuario_actual):
    """Crea una nueva tarea para el usuario autenticado."""
    datos = request.get_json()
    contenido = datos.get('contenido')
    if not contenido:
        return jsonify({'message': 'El contenido de la tarea es requerido'}), 400

    with sqlite3.connect(NOMBRE_BD) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO tareas (contenido, completada, id_usuario) VALUES (?, ?, ?)",
            (contenido, False, usuario_actual[0])
        )
        conn.commit()
        nuevo_id_tarea = cursor.lastrowid
    
    return jsonify({'message': 'Tarea creada exitosamente', 'id': nuevo_id_tarea}), 201

@app.route('/tareas/<int:id_tarea>', methods=['PUT'])
@token_requerido
def actualizar_tarea(usuario_actual, id_tarea):
    """Actualiza el contenido o el estado de una tarea existente."""
    datos = request.get_json()
    contenido = datos.get('contenido')
    completada = datos.get('completada')

    if contenido is None and completada is None:
        return jsonify({'message': 'Se requiere contenido o estado de completada'}), 400

    with sqlite3.connect(NOMBRE_BD) as conn:
        cursor = conn.cursor()
        # Asegurarse de que la tarea pertenece al usuario antes de modificarla
        cursor.execute("SELECT id FROM tareas WHERE id = ? AND id_usuario = ?", (id_tarea, usuario_actual[0]))
        tarea = cursor.fetchone()
        if not tarea:
            return jsonify({'message': 'Tarea no encontrada o no autorizada'}), 404

        if contenido is not None:
            cursor.execute("UPDATE tareas SET contenido = ? WHERE id = ?", (contenido, id_tarea))
        if completada is not None:
            cursor.execute("UPDATE tareas SET completada = ? WHERE id = ?", (bool(completada), id_tarea))
        
        conn.commit()

    return jsonify({'message': 'Tarea actualizada exitosamente'}), 200

@app.route('/tareas/<int:id_tarea>', methods=['DELETE'])
@token_requerido
def eliminar_tarea(usuario_actual, id_tarea):
    """Elimina una tarea existente."""
    with sqlite3.connect(NOMBRE_BD) as conn:
        cursor = conn.cursor()
        # Asegurarse de que la tarea pertenece al usuario antes de eliminarla
        cursor.execute("SELECT id FROM tareas WHERE id = ? AND id_usuario = ?", (id_tarea, usuario_actual[0]))
        tarea = cursor.fetchone()
        if not tarea:
            return jsonify({'message': 'Tarea no encontrada o no autorizada'}), 404

        cursor.execute("DELETE FROM tareas WHERE id = ?", (id_tarea,))
        conn.commit()

    return jsonify({'message': 'Tarea eliminada exitosamente'}), 200

# --- PUNTO DE ENTRADA DE LA APLICACIÓN ---

if __name__ == '__main__':
    # Inicializa la base de datos al arrancar el servidor
    inicializar_bd()
    # Ejecuta la aplicación en modo debug (para desarrollo)
    app.run(debug=True)