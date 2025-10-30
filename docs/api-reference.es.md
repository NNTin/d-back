# Referencia de API

Esta página proporciona documentación completa de la API para d-back, generada automáticamente a partir de los docstrings del código fuente. Todas las clases y métodos incluyen descripciones detalladas, parámetros, valores de retorno y ejemplos.

## Introducción

La API de d-back está organizada en dos componentes principales:

- **WebSocketServer**: La clase principal del servidor para manejar conexiones WebSocket, solicitudes HTTP y difusión de mensajes
- **MockDataProvider**: Proporciona datos simulados y tareas periódicas en segundo plano para desarrollo y pruebas

Toda la documentación de la API sigue docstrings de estilo Google con ejemplos completos. Para patrones de uso y guías de integración, consulte la [Guía del Usuario](user-guide/index.md).

## WebSocketServer

La clase principal del servidor para manejar conexiones WebSocket, solicitudes HTTP y difusión de mensajes. Esta es su interfaz principal para la funcionalidad de d-back.

::: d_back.server.WebSocketServer
    options:
      show_root_heading: true
      show_source: true
      members_order: source
      heading_level: 3

## MockDataProvider

Proporciona datos simulados y tareas periódicas en segundo plano para desarrollo y pruebas. Esta clase se usa automáticamente cuando no se registran callbacks personalizados.

::: d_back.mock.data.MockDataProvider
    options:
      show_root_heading: true
      show_source: true
      members_order: source
      heading_level: 3

## Funciones de Utilidad

Funciones auxiliares para interfaz de línea de comandos y gestión de versiones.

### parse_args

::: d_back.server.parse_args
    options:
      show_root_heading: false
      heading_level: 4

### get_version

::: d_back.server.get_version
    options:
      show_root_heading: false
      heading_level: 4

### main

::: d_back.server.main
    options:
      show_root_heading: false
      heading_level: 4

### main_sync

::: d_back.server.main_sync
    options:
      show_root_heading: false
      heading_level: 4

## Ejemplos de Uso

Para ejemplos prácticos de uso de estas APIs, consulte:

- **[Primeros Pasos](getting-started.md)**: Uso básico y primera conexión
- **[Configuración](user-guide/configuration.md)**: Configuración y ajuste del servidor
- **[Callbacks y Personalización](user-guide/callbacks.md)**: Ejemplos de uso de callbacks
- **[Proveedores de Datos Personalizados](user-guide/custom-data-providers.md)**: Patrones de implementación de proveedores de datos

## Sugerencias de Tipos

Todos los métodos incluyen sugerencias de tipos completas para parámetros y valores de retorno. Al trabajar con callbacks, importe los tipos necesarios:

```python
from typing import Dict, Any, Optional, Tuple, Callable, Awaitable
```

Para más información sobre sugerencias de tipos de Python, consulte la [documentación oficial de typing](https://docs.python.org/3/library/typing.html).
