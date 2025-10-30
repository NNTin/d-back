# Guía del Desarrollador

¡Bienvenido a la guía del desarrollador de d-back! Esta guía proporciona toda la información que necesita para contribuir al proyecto, comprender su arquitectura y seguir las mejores prácticas de desarrollo.

## Introducción

d-back es un servidor WebSocket de código abierto para integración de Discord con simulación de vida ambiental d-zone. Agradecemos contribuciones de la comunidad y esta guía le ayudará a comenzar.

## Primeros Pasos con el Desarrollo

### Configuración del Entorno de Desarrollo

1. **Fork y clone el repositorio**:
   ```bash
   git clone https://github.com/YOUR_USERNAME/d-back.git
   cd d-back
   ```

2. **Crear un entorno virtual**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # En Windows: .venv\Scripts\activate
   ```

3. **Instalar dependencias de desarrollo**:
   ```bash
   pip install -e .[docs]
   pip install pytest pytest-asyncio websockets
   ```

4. **Verificar instalación**:
   ```bash
   python -m d_back --version
   ```

## Arquitectura del Proyecto

### Estructura de Directorios

```
d-back/
├── d_back/               # Código fuente principal
│   ├── __init__.py       # Metadatos del paquete
│   ├── __main__.py       # Punto de entrada CLI
│   ├── server.py         # Clase WebSocketServer principal
│   └── mock/
│       ├── __init__.py
│       └── data.py       # MockDataProvider
├── docs/                 # Documentación MkDocs
│   ├── index.md
│   ├── getting-started.md
│   ├── user-guide/
│   └── api-reference.md
├── tests/                # Pruebas pytest
│   ├── test_dis_connect.py
│   └── helpers/
│       └── mock_websocket_client.py
├── pyproject.toml        # Metadatos del proyecto
├── setup.cfg             # Configuración de setuptools
├── mkdocs.yml            # Configuración de MkDocs
└── README.md
```

### Componentes Principales

**WebSocketServer** (`d_back/server.py`):
- Maneja conexiones WebSocket y solicitudes HTTP
- Gestiona callbacks personalizables para recuperación de datos
- Proporciona métodos de difusión para actualizaciones en tiempo real
- Soporta servicio de archivos estáticos

**MockDataProvider** (`d_back/mock/data.py`):
- Genera datos de usuario y servidor simulados realistas
- Ejecuta tareas periódicas en segundo plano (cambios de presencia, mensajes)
- Proporciona 4 servidores preconfigurados con datos variados
- Usado automáticamente cuando no se registran callbacks personalizados

**Módulo CLI** (`d_back/__main__.py`):
- Parsing de argumentos de línea de comandos
- Punto de entrada para ejecutar el servidor
- Manejo de señales de apagado gracioso

## Pruebas

### Estructura de Pruebas

Las pruebas están organizadas en el directorio `tests/`:

- `test_dis_connect.py`: Pruebas de conectividad WebSocket y flujo de mensajes
- `helpers/mock_websocket_client.py`: Cliente WebSocket simulado para pruebas

### Ejecutar Pruebas

Ejecutar todas las pruebas:
```bash
pytest
```

Ejecutar pruebas específicas:
```bash
pytest tests/test_dis_connect.py
```

Con salida detallada:
```bash
pytest -v
```

Con cobertura:
```bash
pytest --cov=d_back
```

### Escribir Pruebas

Las pruebas usan `pytest` y `pytest-asyncio` para funcionalidad asíncrona:

```python
import pytest
from d_back.server import WebSocketServer

@pytest.mark.asyncio
async def test_server_startup():
    """Test server starts and stops correctly."""
    server = WebSocketServer(port=3001, host="localhost")
    await server.start()
    
    # Test server is running
    assert server.websocket is not None
    
    # Clean shutdown
    await server.stop()
```

## Directrices de Contribución

### Flujo de Trabajo de Git

1. **Crear una rama de característica**:
   ```bash
   git checkout -b feature/mi-nueva-caracteristica
   ```

2. **Hacer cambios y commit**:
   ```bash
   git add .
   git commit -m "Add: Mi nueva característica"
   ```

3. **Push a tu fork**:
   ```bash
   git push origin feature/mi-nueva-caracteristica
   ```

4. **Crear Pull Request** en GitHub

### Formato de Mensaje de Commit

Use mensajes de commit claros y descriptivos:

- `Add: Nueva característica o funcionalidad`
- `Fix: Corrección de bug`
- `Update: Actualización de funcionalidad existente`
- `Docs: Cambios de documentación`
- `Test: Agregar o actualizar pruebas`
- `Refactor: Refactorización de código`

Ejemplos:
```
Add: OAuth2 validation callback support
Fix: WebSocket connection timeout issue
Update: Improve mock data generator performance
Docs: Add custom data providers guide
```

### Estilo de Código

- Seguir [PEP 8](https://pep8.org/) para estilo de código Python
- Usar type hints para parámetros de función y valores de retorno
- Escribir docstrings estilo Google para todas las funciones públicas
- Mantener líneas bajo 100 caracteres cuando sea posible

Ejemplo de docstring:
```python
async def on_get_user_data(self, server_id: str) -> Dict[str, Any]:
    """Retrieve user data for a Discord server.
    
    Args:
        server_id: Discord server ID (snowflake format)
    
    Returns:
        Dictionary mapping user IDs to user data objects
    
    Example:
        ```python
        users = await server.on_get_user_data("232769614004748288")
        ```
    """
    pass
```

## Flujo de Trabajo de Desarrollo

### Ciclo de Desarrollo Local

1. **Hacer cambios de código**
2. **Ejecutar pruebas**: `pytest`
3. **Actualizar documentación** si es necesario
4. **Probar localmente**: `python -m d_back`
5. **Commit y push cambios**

### Construir Documentación Localmente

```bash
# Install docs dependencies
pip install -e .[docs]

# Serve docs with live reload
mkdocs serve

# Build docs
mkdocs build
```

Acceder a docs en `http://127.0.0.1:8000/`

## Traducción de Documentación

### Descripción General

La documentación de d-back está disponible en varios idiomas (English, Spanish, German). Usamos Crowdin para gestionar traducciones de forma colaborativa. El inglés es el idioma fuente: realice los cambios en los archivos en inglés primero. Las traducciones se sincronizan mediante Crowdin y GitHub Actions. El proyecto usa `mkdocs-static-i18n` con la estructura de sufijos (por ejemplo, `index.es.md`, `index.de.md`).

### Configuración del Proyecto Crowdin

1. Crear un proyecto en Crowdin: https://crowdin.com y seleccionar **Markdown** como tipo de archivo.
2. Establecer English como idioma fuente y añadir Spanish (`es`) y German (`de`) como idiomas objetivo.
3. Instalar la aplicación Crowdin GitHub en el repositorio o configurar Crowdin CLI con GitHub Actions. El archivo `crowdin.yml` en la raíz del repositorio define los patrones de archivos y opciones del parser.

Secrets de GitHub necesarios (Repository → Settings → Secrets and variables → Actions):

- `CROWDIN_PROJECT_ID` — ID del proyecto Crowdin
- `CROWDIN_PERSONAL_TOKEN` — Token de acceso personal de Crowdin

### Flujo de Trabajo de Traducción

1. Edite los archivos fuente en inglés (por ejemplo: `docs/index.md`, `docs/getting-started.md`) y envíe un pull request.
2. Tras la fusión en `main`, Crowdin detectará cadenas nuevas o cambiadas y notificará a los traductores.
3. Los traductores traducen el contenido en el editor de Crowdin. Crowdin preserva bloques de código, código en línea y el formato Markdown.
4. Las traducciones se sincronizan de nuevo al repositorio mediante la integración Crowdin ↔ GitHub o GitHub Actions. Crowdin abrirá PRs con las actualizaciones de traducción para que los mantenedores las revisen y fusionen.

### Estructura de Archivos

- Inglés (fuente): `docs/index.md`, `docs/getting-started.md`, `docs/user-guide/configuration.md`
- Spanish: `docs/index.es.md`, `docs/getting-started.es.md`, `docs/user-guide/configuration.es.md`
- German: `docs/index.de.md`, `docs/getting-started.de.md`, `docs/user-guide/configuration.de.md`

### Qué se Traduce

Se debe traducir:

- Texto explicativo, títulos y encabezados
- Mensajes y guías dirigidas al usuario
- Descripciones relacionadas con ejemplos (no los bloques de código)

No se debe traducir:

- Bloques de código e inline code
- Nombres de funciones y clases
- Rutas de archivo y URLs
- Claves y valores de configuración
- Nombres de proyecto y términos técnicos (por ejemplo: d-back, d-zone, WebSocket, OAuth2)

### Archivos Excluidos

Los siguientes archivos están excluidos de la traducción en Crowdin:

- `docs/VERCEL_SETUP.md`
- `docs/TESTING_I18N.md`
- `docs/.pages`
- Archivos de la referencia de la API (generados por mkdocstrings)

### Probar Traducciones Localmente

```bash
# Install documentation dependencies
pip install -e .[docs]

# Serve documentation locally with all languages
mkdocs serve

# Build documentation (generates site/ directory with all languages)
mkdocs build
```

Ver vistas por idioma:

- English: `http://127.0.0.1:8000/`
- Spanish: `http://127.0.0.1:8000/es/`
- German: `http://127.0.0.1:8000/de/`

### Mejores Prácticas de Traducción

- Use un tono formal (usted) en el contenido dirigido a usuarios.
- Mantenga términos técnicos y nombres de proyecto en inglés.
- Preservar el formato Markdown, bloques de código y código en línea.
- Probar localmente las traducciones antes de enviarlas.

### Agregar Nuevos Idiomas

Para añadir un nuevo idioma:

1. Actualice `mkdocs.yml` para incluir el nuevo idioma en la configuración i18n.
2. Actualice `crowdin.yml` con el nuevo `two_letters_code`.
3. Añada el idioma en la configuración del proyecto Crowdin.
4. Cree archivos de traducción iniciales siguiendo el patrón de sufijos.
5. Actualice esta sección con los detalles del nuevo idioma.

### Solución de Problemas

Problemas comunes:

- Traducciones no aparecen en Crowdin: verifique que los patrones en `crowdin.yml` coincidan con los archivos comprometidos y que no estén en `ignore`.
- Traducciones no sincronizan a GitHub: revise los logs de Actions y verifique los secrets `CROWDIN_PROJECT_ID` y `CROWDIN_PERSONAL_TOKEN`.
- Formato roto: revise las traducciones en el editor de Crowdin y compruebe que los bloques de código estén preservados.

### Recursos

- Crowdin documentation: https://support.crowdin.com/
- mkdocs-static-i18n: https://github.com/ultrabug/mkdocs-static-i18n
- Material for MkDocs i18n: https://squidfunk.github.io/mkdocs-material/setup/changing-the-language/


## Depuración

### Registro de Depuración

Agregar declaraciones de impresión o usar logging:

```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

logger.debug("Starting WebSocket server...")
```

### Depurar Conexiones WebSocket

Use la consola del navegador o herramientas WebSocket:

```javascript
const ws = new WebSocket('ws://localhost:3000');
ws.onopen = () => console.log('Connected');
ws.onmessage = (event) => console.log('Received:', event.data);
ws.onerror = (error) => console.error('Error:', error);
```

## Proceso de Lanzamiento

Los lanzamientos son manejados por los mantenedores del proyecto:

1. Actualizar número de versión en `setup.cfg`
2. Actualizar CHANGELOG (si existe)
3. Crear tag de git: `git tag v0.0.X`
4. Push tag: `git push origin v0.0.X`
5. GitHub Actions construye y publica automáticamente a PyPI

### Versionado de Documentación

d-back usa mike para el versionado de documentación, que se integra perfectamente con Material for MkDocs para proporcionar un selector de versiones en la documentación. La estrategia de versionado utiliza tres tipos de versiones:

- **Versiones estables**: Creadas desde tags de git (por ejemplo, 0.0.14, 0.1.0, 1.0.0)
- **Prerelease 'latest'**: Rastrea la rama main (listo para producción pero aún sin etiquetar)
- **Prerelease 'dev'**: Rastrea la rama develop (desarrollo/pruebas)

El selector de versiones aparece en la barra de navegación superior, permitiendo a los usuarios cambiar entre diferentes versiones de la documentación.

#### Estrategia de Versionado

**1. Versiones Estables (desde tags)**

Creadas cuando se etiqueta una nueva versión:

- El número de versión coincide con el tag de git sin el prefijo 'v'
- Estas versiones son permanentes e inmutables
- Ejemplo: El tag v0.0.15 crea la versión de documentación 0.0.15
- Comando: `mike deploy 0.0.15 --push`

**2. Prerelease Latest (rama main)**

Representa el estado actual de la rama main:

- Alias: 'latest'
- Actualizado en cada push a main
- Esta es la versión predeterminada que ven los usuarios
- Comando: `mike deploy <commit-sha> latest --push --update-aliases`

**3. Prerelease Dev (rama develop)**

Representa el estado actual de la rama develop:

- Alias: 'dev'
- Actualizado en cada push a develop
- Usado para probar cambios de documentación antes del lanzamiento
- Comando: `mike deploy <commit-sha> dev --push --update-aliases`

#### Pruebas Locales

Pruebe mike localmente antes de desplegar:

```bash
# Instalar dependencias de documentación (incluye mike)
pip install -e .[docs]

# Desplegar una versión de prueba localmente (no hace push al remoto)
mike deploy 0.0.14-test

# Desplegar con un alias
mike deploy 0.0.15-test latest --update-aliases

# Establecer la versión predeterminada (lo que los usuarios ven al visitar los docs)
mike set-default latest

# Listar todas las versiones desplegadas
mike list

# Servir la documentación versionada localmente
mike serve
# Visite http://localhost:8000 para probar
# Use el selector de versiones en la navegación superior para cambiar entre versiones

# Eliminar una versión de prueba
mike delete 0.0.14-test
```

**Notas importantes para pruebas locales:**

- Mike crea una rama `gh-pages` localmente para almacenar la documentación versionada
- Use nombres de versión de prueba (por ejemplo, 0.0.14-test) para evitar conflictos con versiones de producción
- La bandera `--push` se omite durante las pruebas locales para prevenir despliegues accidentales
- Siempre pruebe la funcionalidad del selector de versiones antes de desplegar
- Verifique que los tres idiomas (English, Spanish, German) funcionen correctamente en cada versión

#### Alias de Versiones

Los alias son nombres simbólicos que apuntan a versiones específicas:

- Alias comunes: 'latest' (rama main), 'dev' (rama develop), 'stable' (última versión estable)
- Los alias pueden actualizarse para apuntar a diferentes versiones
- Ejemplo: Después de lanzar 0.1.0, actualice el alias 'stable': `mike deploy 0.1.0 stable --update-aliases`
- La bandera `--update-aliases` actualiza alias existentes en lugar de crear duplicados

#### Flujo de Trabajo de Despliegue

Proceso de despliegue manual (para pruebas locales o cuando sea necesario):

**Para lanzamientos estables:**
```bash
# Después de crear un tag de git (por ejemplo, v0.0.15)
mike deploy 0.0.15 stable --push --update-aliases
mike set-default latest --push
```

**Para actualizaciones de la rama main:**
```bash
# Después de fusionar a main
mike deploy <commit-sha> latest --push --update-aliases
```

**Para actualizaciones de la rama develop:**
```bash
# Después de fusionar a develop
mike deploy <commit-sha> dev --push --update-aliases
```

**Nota:** Estos comandos son para despliegue manual. El despliegue automatizado mediante GitHub Actions es el enfoque recomendado para producción (vea "Despliegue Automatizado con GitHub Actions" más abajo).

#### Despliegue Automatizado con GitHub Actions

El despliegue de la documentación está automatizado mediante GitHub Actions. El workflow está definido en `.github/workflows/docs.yml` y maneja todos los despliegues de producción.

**Descripción General:**

- La documentación se despliega automáticamente en pushes a main, develop y creación de tags
- El workflow gestiona el versionado con mike y despliega a GitHub Pages
- El despliegue manual usando mike localmente sigue disponible para pruebas
- Los tres idiomas (inglés, español, alemán) se construyen y despliegan juntos

**Activadores Automáticos:**

1. **Creación de tag (v*)**: Crea una versión estable
   - Ejemplo: Tag `v0.0.15` despliega versión `0.0.15` con alias `stable`
   - Las versiones estables son permanentes e inmutables
   - Comando ejecutado: `mike deploy 0.0.15 stable --push --update-aliases`

2. **Push a main**: Despliega prerelease 'latest'
   - Representa el estado actual listo para producción
   - Se establece como la versión predeterminada que ven los usuarios
   - Comando ejecutado: `mike deploy <commit-sha> latest --push --update-aliases`

3. **Push a develop**: Despliega prerelease 'dev'
   - Representa el estado actual de desarrollo
   - Se usa para probar cambios de documentación antes del lanzamiento
   - No se establece como predeterminado (dev es solo para pruebas)
   - Comando ejecutado: `mike deploy <commit-sha> dev --push --update-aliases`

4. **Activación manual**: Disponible mediante `workflow_dispatch` en la interfaz de GitHub Actions
   - Útil para pruebas o re-despliegue de documentación
   - Acceso mediante: Repositorio → pestaña Actions → workflow Documentation → Run workflow

**Proceso del Workflow:**

1. **Checkout repository**: Obtiene el historial completo de git (requerido para que mike acceda a la rama gh-pages)
2. **Set up Python 3.11**: Instala Python con caché de pip para construcciones más rápidas
3. **Install dependencies**: Ejecuta `pip install -e .[docs]` para instalar mkdocs-material, mkdocs-static-i18n, mkdocstrings y mike desde setup.cfg
4. **Configure git**: Configura el usuario de git para commits automatizados a la rama gh-pages
5. **Determine version**: Analiza el tipo de activador (tag, main o develop) para decidir la estrategia de despliegue
6. **Deploy with mike**: Ejecuta el comando mike apropiado para desplegar documentación versionada a la rama gh-pages
7. **GitHub Pages sirve documentación actualizada**: Los cambios aparecen en 1-2 minutos en https://nntin.github.io/d-back/

**Estrategia de Versiones:**

- **Versiones estables** (desde tags): Permanentes, inmutables, representan lanzamientos oficiales
- **Alias 'latest'**: Actualizado en cada push a la rama main, establecido como predeterminado para usuarios
- **Alias 'dev'**: Actualizado en cada push a la rama develop, solo para pruebas
- El selector de versión en la navegación de la documentación muestra todas las versiones disponibles

**Monitoreo de Despliegues:**

- **Ver ejecuciones de workflow**: Repositorio → pestaña Actions → workflow Documentation
- **Verificar estado de despliegue**: Ver el badge Documentation Status en README.md
- **Logs de workflow**: Información detallada de despliegue disponible en cada ejecución de workflow
- **Despliegues fallidos**: Los mensajes de error aparecen en los logs de workflow con información para solución de problemas

**Configuración de GitHub Pages:**

Configuración inicial (solo se necesita una vez):

1. Ir a: Repository Settings → Pages
2. Establecer Source: Deploy from a branch
3. Establecer Branch: `gh-pages` (creado automáticamente por la primera ejecución del workflow)
4. Hacer clic en Save
5. La documentación estará disponible en: https://nntin.github.io/d-back/
6. Los cambios aparecen en 1-2 minutos después de completarse el workflow

**Despliegue Manual (si es necesario):**

El workflow automatizado maneja la mayoría de escenarios de despliegue. El despliegue manual puede ser necesario para:

- Probar cambios de documentación localmente antes de hacer push
- Solucionar problemas de despliegue que requieran troubleshooting local
- Desplegar desde una rama local para propósitos de prueba

Use los comandos mike documentados en la subsección "Flujo de Trabajo de Despliegue" arriba para despliegue manual.

**Solución de Problemas del Workflow:**

**Problema:** El workflow falla en git push a gh-pages
- **Solución**: Verifique que Actions tenga permisos de escritura
  - Ir a: Settings → Actions → General → Workflow permissions
  - Seleccionar: "Read and write permissions"
  - Hacer clic en Save

**Problema:** La versión desplegada no aparece en el selector de versión
- **Solución**: Verifique que la condición del activador coincidió con la rama o tag esperado
- **Solución**: Revise los logs de workflow para confirmar que el despliegue se completó exitosamente
- **Solución**: Asegúrese de que al menos dos versiones estén desplegadas para que aparezca el selector

**Problema:** Contenido antiguo aparece en versión recién desplegada
- **Solución**: Limpie la caché del navegador y recargue
- **Solución**: Verifique que el workflow se completó exitosamente en la pestaña Actions
- **Solución**: Verifique que se desplegó la versión correcta revisando los logs de workflow

**Problema:** La rama gh-pages no se creó
- **Solución**: Revise los logs de workflow para errores durante el primer despliegue
- **Solución**: Verifique que Actions tenga permisos de escritura (vea el primer problema arriba)
- **Solución**: Active manualmente el workflow mediante workflow_dispatch para reintentar

#### Mejores Prácticas

- Siempre pruebe localmente con `mike serve` antes de desplegar
- Use versionado semántico para lanzamientos estables (MAJOR.MINOR.PATCH)
- Mantenga 'latest' como la versión predeterminada para los usuarios
- Documente cambios importantes en notas de lanzamiento específicas de versión
- Mantenga al menos las últimas 3 versiones estables como referencia
- Elimine versiones muy antiguas para mantener la lista de versiones manejable: `mike delete 0.0.1 --push`
- Verifique que el soporte multilingüe funcione en todas las versiones desplegadas

#### Solución de Problemas

**Problema:** El selector de versiones no aparece
- Solución: Verifique que `extra.version.provider: mike` esté configurado en mkdocs.yml (ya configurado en línea 137)
- Solución: Asegúrese de que al menos dos versiones estén desplegadas
- Solución: Verifique que el tema Material esté configurado correctamente

**Problema:** Las versiones no se despliegan
- Solución: Asegúrese de que mike esté instalado: `pip install -e .[docs]`
- Solución: Verifique que la rama gh-pages exista
- Solución: Verifique que el remoto de git esté configurado correctamente

**Problema:** Conflictos entre selector de idioma y selector de versión
- Solución: Ambos selectores deberían funcionar juntos; verifique la configuración de mkdocs-static-i18n
- Solución: Pruebe con `mike serve` para asegurar que ambos selectores aparezcan

**Problema:** Contenido antiguo aparece en nueva versión
- Solución: Use `mike deploy --update-aliases` para actualizar alias
- Solución: Limpie la caché del navegador
- Solución: Reconstruya con `mkdocs build --clean` antes de desplegar

#### Recursos

- Mike documentation: https://github.com/jimporter/mike
- Material for MkDocs versioning: https://squidfunk.github.io/mkdocs-material/setup/setting-up-versioning/
- Semantic Versioning: https://semver.org/

**Nota:** GitHub Actions automatizará este proceso en una fase futura, desplegando automáticamente 'dev' en pushes a la rama develop, 'latest' en pushes a la rama main, y versiones estables en la creación de tags.

## Mejoras Futuras

Áreas donde agradecemos contribuciones:

- **Soporte Redis**: Cacheo y pub/sub distribuido
- **Métricas y Monitoreo**: Prometheus/Grafana integration
- **Autenticación mejorada**: Más proveedores OAuth2
- **Gestión de sesiones**: Persistencia y renovación de sesiones
- **Pruebas de carga**: Pruebas de rendimiento y benchmark
- **Internacionalización**: Mensajes de error multilenguaje

## Obtener Ayuda

¿Necesita ayuda con desarrollo?

- **GitHub Issues**: Reportar bugs o solicitar características
- **GitHub Discussions**: Hacer preguntas o discutir ideas
- **Documentación**: Revisar [User Guide](../user-guide/index.md) y [API Reference](../api-reference.md)
- **Código fuente**: Leer el código en [GitHub](https://github.com/NNTin/d-back)

## Licencia

d-back está licenciado bajo la Licencia MIT. Consulte el archivo LICENSE para detalles.

## ¿Qué Sigue?

- **[Guía del Usuario](../user-guide/index.md)**: Aprender cómo usar d-back
- **[Referencia de API](../api-reference.md)**: Documentación detallada de la API
- **[Primeros Pasos](../getting-started.md)**: Instalar y ejecutar d-back
