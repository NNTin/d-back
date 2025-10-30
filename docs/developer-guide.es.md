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
