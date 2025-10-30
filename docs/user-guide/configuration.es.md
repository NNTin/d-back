# Configuración

Esta guía cubre todas las formas en que puede configurar d-back para adaptarlo a sus necesidades, desde opciones de línea de comandos hasta configuraciones programáticas y variables de entorno.

## Introducción

d-back ofrece opciones de configuración flexibles para adaptarse a diferentes escenarios de despliegue. Ya sea que lo esté ejecutando desde la línea de comandos durante el desarrollo o integrándolo en una aplicación Python más grande, tiene control total sobre el comportamiento del servidor, configuraciones de red y servicio de archivos estáticos.

## Opciones de Línea de Comandos {#command-line-options}

Al ejecutar d-back desde la línea de comandos, puede personalizar su comportamiento usando varias opciones:

### Opciones Disponibles

| Opción | Predeterminado | Descripción | Ejemplo |
|--------|---------|-------------|---------|
| `--port` | `3000` | Puerto en el que ejecutar el servidor WebSocket | `d_back --port 8080` |
| `--host` | `localhost` | Host al que vincular el servidor | `d_back --host 0.0.0.0` |
| `--static-dir` | Integrado | Directorio desde el cual servir archivos estáticos | `d_back --static-dir ./my-frontend-build` |
| `--version` | - | Mostrar información de versión | `d_back --version` |

### Ejemplos de Uso

**Inicio predeterminado** (localhost:3000):
```bash
d_back
```

**Host y puerto personalizados**:
```bash
d_back --host 0.0.0.0 --port 8080
```

Esto hace que el servidor sea accesible desde otras máquinas en su red.

**Directorio estático personalizado**:
```bash
d_back --static-dir ./my-frontend-build
```

Sirva sus propios archivos de frontend en lugar de la interfaz d-zone integrada.

**Obtener ayuda**:
```bash
d_back --help
```

Mostrar todas las opciones de línea de comandos disponibles.

**Verificar versión**:
```bash
d_back --version
```

!!! note "Ejecutar como Módulo"
    También puede ejecutar d-back como un módulo de Python con las mismas opciones:
    ```bash
    python -m d_back --host 0.0.0.0 --port 8080
    ```

## Configuración Programática

Para más control e integración en sus aplicaciones Python, puede configurar d-back programáticamente:

```python
import asyncio
from d_back.server import WebSocketServer

async def main():
    # Create server instance with custom settings
    server = WebSocketServer(port=3000, host="localhost")
    
    # Configure callbacks (optional)
    server.on_get_user_data(my_user_data_callback)
    server.on_get_server_data(my_server_data_callback)
    
    # Start the server
    print("Starting d-back server...")
    await server.start()

asyncio.run(main())
```

### Parámetros del Constructor

La clase `WebSocketServer` acepta los siguientes parámetros:

- **`port`** (int, opcional): El número de puerto en el que escuchar. Predeterminado a `3000`.
- **`host`** (str, opcional): El nombre de host o dirección IP a la que vincular. Predeterminado a `"localhost"`.

### Cuándo Usar Configuración Programática

Use configuración programática cuando:

- Necesite integrar d-back en una aplicación Python más grande
- Quiera configurar dinámicamente ajustes basados en condiciones de tiempo de ejecución
- Necesite acceder a métodos y atributos de la instancia del servidor
- Quiera implementar lógica personalizada de inicio/apagado

### Acceso a Atributos del Servidor

Una vez que cree una instancia de `WebSocketServer`, puede acceder a varios atributos:

```python
server = WebSocketServer(port=3000, host="localhost")

# Access configuration
print(f"Server will run on {server.host}:{server.port}")

# Access connections (set of connected WebSocket clients)
print(f"Active connections: {len(server.connections)}")

# Access data provider
print(f"Using data provider: {server.data_provider}")
```

## Variables de Entorno

Aunque d-back no usa variables de entorno por defecto, puede extenderlo fácilmente para soportar configuración basada en entorno:

```python
import os
from d_back.server import WebSocketServer

# Example: Use environment variables
port = int(os.getenv('D_BACK_PORT', 3000))
host = os.getenv('D_BACK_HOST', 'localhost')

server = WebSocketServer(port=port, host=host)
```

### Variables de Entorno Recomendadas

Aquí hay un patrón sugerido para nombrar variables de entorno:

| Variable de Entorno | Tipo | Predeterminado | Descripción |
|---------------------|------|---------|-------------|
| `D_BACK_PORT` | int | `3000` | Puerto del servidor |
| `D_BACK_HOST` | str | `localhost` | Host del servidor |
| `D_BACK_STATIC_DIR` | str | Integrado | Directorio de archivos estáticos |

### Ejemplo: Integración Completa de Variables de Entorno

```python
import os
import asyncio
from pathlib import Path
from d_back.server import WebSocketServer

async def main():
    # Read configuration from environment
    port = int(os.getenv('D_BACK_PORT', 3000))
    host = os.getenv('D_BACK_HOST', 'localhost')
    static_dir = os.getenv('D_BACK_STATIC_DIR')
    
    # Create server
    server = WebSocketServer(port=port, host=host)
    
    # Configure static directory if provided
    if static_dir:
        server.static_dir = Path(static_dir)
    
    # Start server
    await server.start()

if __name__ == '__main__':
    asyncio.run(main())
```

!!! tip "Flexibilidad de Despliegue"
    Usar variables de entorno facilita desplegar d-back en diferentes entornos (desarrollo, staging, producción) sin cambios de código.

## Servicio de Archivos Estáticos {#static-file-serving}

d-back incluye un servidor HTTP integrado para servir archivos estáticos, facilitando la entrega de su frontend d-zone u otros activos web.

### Comportamiento Predeterminado

Por defecto, d-back sirve archivos estáticos desde su directorio `dist/` integrado, que contiene el frontend d-zone.

### Directorio Estático Personalizado

Para servir sus propios archivos estáticos:

**Línea de comandos**:
```bash
d_back --static-dir ./my-frontend-build
```

**Programático**:
```python
from pathlib import Path
server = WebSocketServer(port=3000, host="localhost")
server.static_dir = Path("./my-frontend-build")
```

### Requisitos

El servicio de archivos estáticos requiere **websockets versión 10.0 o superior** para soporte del protocolo HTTP. Esto es manejado automáticamente por las dependencias de d-back.

### Seguridad

d-back incluye protección contra path traversal para prevenir acceso a archivos fuera del directorio estático. Solicitudes como `/../../../etc/passwd` se bloquean automáticamente.

!!! warning "Nota de Seguridad"
    Siempre asegúrese de que su directorio estático no contenga archivos sensibles. Solo sirva archivos que estén destinados a ser públicamente accesibles.

### Tipos de Archivo

El servidor detecta automáticamente tipos de contenido basados en extensiones de archivo:

- `.html` → `text/html`
- `.css` → `text/css`
- `.js` → `application/javascript`
- `.json` → `application/json`
- `.png`, `.jpg`, `.gif` → Tipos de imagen apropiados
- Y más...

## Configuración de Servidor Simulado

d-back viene con servidores de Discord simulados preconfigurados para desarrollo y pruebas. Estos servidores proporcionan datos de usuario realistas sin requerir credenciales de la API de Discord.

### Servidores Simulados Disponibles

| Nombre del Servidor | ID del Servidor | Descripción | Cantidad de Usuarios |
|-------------|-----------|-------------|------------|
| **servidor d-world** | `232769614004748288` | Servidor de desarrollo principal con actividad de usuario diversa | 4 usuarios |
| **servidor docs** | `482241773318701056` | Servidor de documentación con actividad moderada | 1 usuario |
| **servidor oauth2** | `123456789012345678` | Servidor protegido para probar flujos OAuth2 | 1 usuario |
| **servidor my repos** | `987654321098765432` | Servidor de exhibición de repositorios | 21 usuarios |

### Usar Servidores Simulados

Los servidores simulados están disponibles automáticamente cuando inicia d-back. Puede solicitar datos para cualquiera de estos servidores usando su ID de servidor:

```javascript
// JavaScript WebSocket client example
socket.send(JSON.stringify({
    type: 'get_user_data',
    serverId: '232769614004748288'  // d-world server
}));
```

### Características de Datos Simulados

Los datos simulados incluyen:

- **Estados de usuario**: online, idle, dnd (do not disturb), offline
- **Colores de roles**: Códigos de color hexadecimales para representación visual
- **Nombres realistas**: Nombres de usuario variados estilo Discord
- **Actualizaciones dinámicas**: Cambios de estado y mensajes ocurren periódicamente

!!! note "Solo Desarrollo"
    Los servidores simulados están diseñados para desarrollo y pruebas. Para despliegues de producción, implemente proveedores de datos personalizados para usar datos reales de Discord. Consulte la guía [Proveedores de Datos Personalizados](custom-data-providers.md).

## Ciclo de Vida del Servidor

Comprender el ciclo de vida del servidor le ayuda a gestionar inicio, operación y apagado efectivamente.

### Iniciar el Servidor

**Método 1: `start()`**
```python
await server.start()
```
Inicia el servidor WebSocket y el listener HTTP. Este método retorna inmediatamente después del inicio, permitiéndole realizar operaciones adicionales.

**Método 2: `run_forever()`**
```python
await server.run_forever()
```
Inicia el servidor y lo ejecuta indefinidamente hasta ser interrumpido. Esto es útil para scripts de servidor simples.

### Detener el Servidor

**Apagado gracioso:**
```python
await server.stop()
```
Cierra todas las conexiones activas y detiene el servidor limpiamente.

**Manejo de señales:**
El servidor maneja automáticamente `Ctrl+C` (SIGINT) para apagado gracioso. Cuando presiona `Ctrl+C`, el servidor:

1. Deja de aceptar nuevas conexiones
2. Cierra conexiones existentes graciosamente
3. Limpia recursos
4. Sale

### Ejemplo Completo de Ciclo de Vida

```python
import asyncio
import signal
from d_back.server import WebSocketServer

async def main():
    server = WebSocketServer(port=3000, host="localhost")
    
    # Setup signal handler for graceful shutdown
    loop = asyncio.get_event_loop()
    
    def signal_handler():
        print("\nReceived shutdown signal...")
        asyncio.create_task(server.stop())
    
    loop.add_signal_handler(signal.SIGINT, signal_handler)
    loop.add_signal_handler(signal.SIGTERM, signal_handler)
    
    # Start server
    print("Starting server...")
    await server.start()
    
    # Run forever
    await server.run_forever()

asyncio.run(main())
```

## Mejores Prácticas

Siga estas recomendaciones para una configuración óptima de d-back:

### Configuración de Red

!!! tip "Desarrollo vs Producción"
    - **Desarrollo**: Use `localhost` para restringir acceso solo a su máquina
    - **Producción**: Use `0.0.0.0` para aceptar conexiones desde cualquier interfaz de red

!!! warning "Selección de Puerto"
    - Evite puertos privilegiados (`<1024`) a menos que ejecute con permisos apropiados
    - Puertos comunes como `3000`, `8080` o `8000` son buenas opciones
    - Verifique que su puerto elegido no esté ya en uso

### Archivos Estáticos

- **Organice**: Mantenga archivos estáticos en un directorio dedicado
- **Estructura**: Use estructura estándar de proyecto web (`index.html`, `css/`, `js/`, etc.)
- **Proceso de build**: Si usa un framework de frontend, configure su salida de build al directorio estático

### Gestión de Configuración

- **Use variables de entorno** para configuraciones específicas de despliegue
- **Use configuración programática** para configuraciones complejas o dinámicas
- **Documente su configuración** en README o guías de despliegue
- **Mantenga secretos seguros**: Nunca codifique en duro claves de API o tokens

### Rendimiento

- **Límites de conexión**: Monitoree el número de conexiones activas
- **Uso de recursos**: Rastree uso de memoria y CPU bajo carga
- **Registro**: Implemente registro apropiado para depuración y monitoreo

!!! example "Ejemplo de Configuración de Producción"
    ```python
    import os
    from d_back.server import WebSocketServer
    
    # Production-ready configuration
    server = WebSocketServer(
        port=int(os.getenv('PORT', 3000)),
        host='0.0.0.0'  # Accept external connections
    )
    
    # Configure callbacks for real data
    server.on_get_user_data(real_discord_data_provider)
    server.on_validate_discord_user(oauth2_validator)
    
    # Start server
    await server.start()
    ```

## ¿Qué Sigue?

Ahora que comprende cómo configurar d-back, aprenda cómo personalizar su comportamiento:

- **[Callbacks y Personalización](callbacks.md)**: Anule el comportamiento predeterminado con callbacks personalizados
- **[Proveedores de Datos Personalizados](custom-data-providers.md)**: Reemplace datos simulados con fuentes reales
- **[Referencia de API](../api-reference.md)**: Documentación detallada de la API
