# 🤖 Controlador de Versiones de Asistentes OpenAI

## 📖 Descripción

Este proyecto está diseñado para **versionar las configuraciones de tus asistentes de OpenAI**.

Registra automáticamente las configuraciones (`config`) de uno o más asistentes en un repositorio de **GitHub** cada vez que se detecta un cambio.  
Esto garantiza una **trazabilidad completa**, permitiéndote **revertir** el estado de un asistente a versiones anteriores que produjeron resultados óptimos.

---

## ⚙️ Instalación

Este proyecto utiliza **Poetry** para la gestión de dependencias y la creación de entornos virtuales aislados.

### 1. Requisitos

Asegúrate de tener instalados los siguientes componentes:

- **Python:** Versión **3.7 o superior**  
- **Git:** Para clonar el repositorio y gestionar *commits*  
- **Poetry:** Si no lo tienes, puedes instalarlo con el comando oficial (Windows PowerShell):

  ```powershell
  (Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -
  ```

### 2. Configuración e inicio

Una vez tengas Poetry y Git, sigue estos pasos:

1. **Clona el repositorio:**
   ```bash
   git clone https://github.com/Jinerson/control_versiones.git
   cd control_versiones
   ```

2. **Instala las dependencias:**
   ```bash
   poetry install
   ```

3. **Activa el entorno (opcional):**  
   Si deseas trabajar directamente dentro del entorno virtual de Poetry, ejecuta:
   ```bash
   poetry env activate
   ```

---

## 🔒 Configuración inicial

El proyecto requiere la configuración de varias variables de entorno en un archivo **`.env`** para autenticarse con OpenAI y GitHub.

### 1. Configurar la clave de OpenAI (`OPENAI_API_KEY`)

Por seguridad, la clave de acceso a OpenAI se gestiona mediante el archivo `.env`.

- Obtén tu **API Key** desde la plataforma de OpenAI. **No la compartas con nadie.**
- Agrega la variable **`OPENAI_API_KEY`** al archivo **`.env`** en la carpeta principal del proyecto:

  ```
  OPENAI_API_KEY=aqui_va_tu_clave_de_openai
  ```

### 2. Configurar acceso a GitHub

Para que el programa pueda realizar *commits* automáticamente al repositorio de versionado, necesitas configurar un **Token de Acceso Personal**.

#### A. Crear repositorio y token

1. **Crea el repositorio** en GitHub donde se guardarán los *commits* de versión (el repositorio destino).  
2. **Genera un Fine-Grained Personal Access Token** en GitHub:  
   `Settings > Developer Settings > Personal access tokens`.  
   Asegúrate de:
   - Asignarle acceso solo al repositorio **seleccionado** (el que acabas de crear).
   - En la sección de permisos (**Permissions**), otorgar acceso de **Read and Write** al permiso **Contents**.

#### B. Variables de entorno de GitHub

Agrega las siguientes variables al archivo **`.env`**.  
**No uses espacios** antes o después del signo igual.

```
# Tu nombre de usuario de GitHub
GITHUB_USER=nombre_de_usuario

# El token que acabas de generar
GITHUB_TOKEN=token_creado

# La URL HTTPS del repositorio de destino
# (Ejemplo: https://github.com/usuario/mi-repo-versionado.git)
GITHUB_REPO_URL=https://github.com/tu_usuario/tu_repositorio.git
```

> ⚠️ **Advertencia:** El programa **no iniciará** si alguna de estas variables no está configurada correctamente, ya que no podrá realizar los *commits* de control de versiones.

---

## 🚀 Uso

> ⚠️ **Advertencia:** El programa requiere una conexión a internet estable.

Una vez que la instalación y la configuración estén completas, sigue estos pasos para ejecutar el controlador de versiones:

```bash
poetry run python src/proyecto_1/main.py
```

---

## 🗑️ Archivo `.gitignore`

Es crucial que **no subas información sensible** (como claves de API) o archivos temporales generados por el sistema a tu repositorio de GitHub.  

Asegúrate de que tu archivo **`.gitignore`** en la raíz del proyecto contenga las siguientes exclusiones:

```
# Archivos de configuración de entorno (CRUCIAL para seguridad)
.env

# Carpetas de entorno de desarrollo
.vscode/

# Directorios y archivos generados por Python
src/modules/__pycache__/
src/__pycache__/

# Directorio de entorno virtual de Poetry
.venv/

# Carpeta de tests (solo contiene tests locales que no quieres versionar)
tests/
```

**Nota:**  
Inicialmente, solo se versionará la carpeta **`Asistentes`**, mientras que las demás rutas estarán incluidas en el archivo **`.gitignore`**.  
Si deseas realizar *commits* de todos los archivos del proyecto, elimina las rutas correspondientes del archivo **`.gitignore`**.
