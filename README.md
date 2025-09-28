# PFO2: Sistema de Gestión de Tareas con API REST y Frontend Web

Este proyecto es una aplicación web completa para la gestión de tareas. Cumple con los requisitos del Trabajo Práctico Obligatorio (PFO2), implementando un backend con una API RESTful en Flask y un frontend web interactivo.

## Estructura del Proyecto

El proyecto está organizado en dos carpetas principales:

-   `backend/`: Contiene el servidor Flask (`servidor.py`), que gestiona la lógica de negocio, la API y la interacción con la base de datos. También incluye el archivo `requirements.txt` para las dependencias de Python.
-   `frontend/`: Contiene todos los archivos del cliente web (HTML, CSS, y JavaScript), estructurados para ofrecer una experiencia de usuario fluida y multipágina.

## Características Implementadas

-   **API RESTful Completa:** Endpoints para la gestión de usuarios y tareas.
-   **Gestión de Usuarios:**
    -   Registro con contraseña hasheada y preguntas de seguridad predefinidas.
    -   Inicio de sesión mediante credenciales que genera un Token JWT para autenticación.
    -   Recuperación de contraseña validando la respuesta de seguridad.
-   **Gestión de Tareas (CRUD):**
    -   Crear, leer, actualizar y eliminar tareas por usuario.
    -   Marcar/desmarcar tareas como completadas usando un checkbox interactivo.
-   **Frontend Web Moderno:**
    -   Interfaz limpia y amigable construida con HTML5, CSS3 y JavaScript.
    -   Diseño responsivo y mejoras visuales como fuentes modernas, sombreados y una paleta de colores cohesiva.
    -   Navegación fluida entre las páginas de login, registro, recuperación y la lista de tareas.

## Requisitos Previos

-   Python 3.x
-   `pip` (gestor de paquetes de Python)

## Instalación y Ejecución

Siga estos pasos para poner en marcha el proyecto:

**1. Configurar el Backend**

Navegue a la carpeta del backend e instale las dependencias:

```bash
# Navegar a la carpeta del backend
cd backend

# Instalar las dependencias desde requirements.txt
py -m pip install -r requirements.txt
```

**2. Iniciar el Servidor**

Una vez instaladas las dependencias y aún dentro de la carpeta `backend`, inicie el servidor Flask:

```bash
# Ejecutar el servidor
py servidor.py
```

El servidor se ejecutará en `http://127.0.0.1:5000`. La primera vez que se inicie, creará automáticamente la base de datos `tasks.db`.

**3. Usar la Aplicación Web**

Abra el archivo `frontend/index.html` en su navegador web. Será redirigido automáticamente a la página de inicio de sesión o a su lista de tareas si ya tiene una sesión activa.

## Capturas de Pantalla

*(Aquí puedes añadir capturas de pantalla de la aplicación funcionando. Por ejemplo: la página de login, el registro con las preguntas de seguridad, y la lista de tareas con algunas tareas añadidas y una marcada como completada).*

![Inicio sesion](\static\img\inicio.png)


![Registro](static\img\registro.png)

![Registro](static\img\recuperar.png)

![Registro](static\img\recuperar2.png)

![Registro](static\img\tareas.png)

## Publicación en GitHub Pages

Para alojar el frontend en GitHub Pages:

1.  Suba la **totalidad del contenido de la carpeta `frontend`** a la raíz de su repositorio de GitHub (o a una carpeta `/docs` si lo prefiere).
2.  En la configuración de su repositorio, vaya a la sección "Pages".
3.  Seleccione la rama y la carpeta donde subió los archivos.
4.  Guarde los cambios. Su cliente web estará disponible en `https://<su-usuario>.github.io/<su-repositorio>/`.

**Importante:** Para que el cliente en GitHub Pages funcione, necesitará tener el `servidor.py` corriendo en un servicio accesible públicamente (como Heroku, PythonAnywhere, etc.) y actualizar la variable `BASE_URL` en `script.js` para que apunte a la URL de su servidor público.

## Respuestas Conceptuales

### 1. ¿Por qué es importante hashear las contraseñas?

Es crucial hashear las contraseñas antes de almacenarlas en una base de datos por varias razones de seguridad:

-   **Protección contra robos de datos:** Si un atacante logra acceder a la base de datos, no podrá ver las contraseñas de los usuarios en texto plano. El hash es un proceso unidireccional, lo que significa que es computacionalmente inviable revertirlo para obtener la contraseña original.
-   **Confidencialidad del usuario:** Los usuarios a menudo reutilizan contraseñas en múltiples servicios. Si una contraseña se filtra de un sistema, los atacantes podrían usarla para intentar acceder a otras cuentas del mismo usuario. Al hashear las contraseñas, se protege la privacidad y seguridad del usuario más allá de nuestra aplicación.
-   **Cumplimiento de normativas:** Muchas regulaciones de protección de datos, como el GDPR, exigen que se tomen medidas adecuadas para proteger los datos personales, y el almacenamiento de contraseñas en texto plano es una clara violación de este principio.

### 2. ¿Cuáles son las ventajas de usar SQLite en este proyecto?

SQLite es una excelente elección para este proyecto por las siguientes ventajas:

-   **Cero configuración y simplicidad:** SQLite es una base de datos "sin servidor", lo que significa que no requiere un proceso de servidor separado. La base de datos es un único archivo en el disco (`tasks.db` en nuestro caso), lo que simplifica enormemente la configuración y el despliegue.
-   **Portabilidad:** Al ser un solo archivo, la base de datos es extremadamente portátil. Es ideal para desarrollo, pruebas y aplicaciones de pequeña a mediana escala.
-   **Ligereza:** SQLite es muy ligero en términos de consumo de recursos, lo que lo hace perfecto para el desarrollo local sin sobrecargar la máquina.
-   **Integración con Python:** La biblioteca `sqlite3` viene incluida en la instalación estándar de Python, por lo que no es necesario instalar componentes adicionales, simplificando la configuración del proyecto.
