# Primeros Pasos

¡Bienvenido a d-back! Esta guía le ayudará a ponerse en marcha con el servidor WebSocket que impulsa la simulación de vida ambiental d-zone. Al final de esta guía, tendrá d-back instalado y sirviendo datos simulados de Discord a través de conexiones WebSocket.

## Requisitos Previos

Antes de comenzar, asegúrese de tener lo siguiente:

- **Python 3.8 o superior** instalado en su sistema
- **Gestor de paquetes pip** (generalmente viene con Python)
- **Comprensión básica de async/await en Python** (útil pero no requerido)
- **Git** (opcional, solo necesario si instala desde el código fuente)

## Instalación

d-back puede instalarse de varias maneras. Elija el método que mejor se ajuste a sus necesidades:

### Desde PyPI (Recomendado)

La forma más fácil de instalar d-back es desde el Índice de Paquetes de Python:

```bash
pip install d-back
```

### Desde el Código Fuente

Para la versión de desarrollo más reciente o si desea contribuir:

1. Clone el repositorio:
   ```bash
   git clone https://github.com/NNTin/d-back.git
   cd d-back
   ```

2. Cree un entorno virtual (recomendado):

   === "Windows"
       ```bash
       python -m venv .venv
       .venv\Scripts\activate
       ```

   === "macOS/Linux"
       ```bash
       python3 -m venv .venv
       source .venv/bin/activate
       ```

3. Instale en modo desarrollo:
   ```bash
   pip install -e .
   ```

### Con Dependencias de Documentación

Si planea construir la documentación localmente:

```bash
pip install d-back[docs]
```

O desde el código fuente:

```bash
pip install -e .[docs]
```

## Verificar Instalación

Después de la instalación, verifique que d-back esté correctamente instalado:

```bash
d_back --version
```

Debería ver una salida similar a:

```
d-back version 0.0.14
```

!!! tip "Solución de Problemas"
    Si el comando `d_back` no se encuentra, asegúrese de que su directorio de scripts de Python esté en su PATH. Alternativamente, puede ejecutar d-back como un módulo de Python: `python -m d_back --version`

## Inicio Rápido

¡Ahora que d-back está instalado, pongámoslo en marcha!

### Enfoque de Línea de Comandos

La forma más simple de iniciar el servidor es con la configuración predeterminada:

```bash
# Start with defaults (localhost:3000)
d_back
```

O ejecútelo como un módulo de Python:

```bash
python -m d_back
```

Debería ver una salida de consola similar a:

```
WebSocket server started on ws://localhost:3000
Serving static files from: /path/to/d_back/dist
Press Ctrl+C to stop the server
```

!!! note "Configuración Predeterminada"
    Por defecto, d-back se ejecuta en `localhost:3000` y sirve el frontend d-zone integrado desde archivos estáticos.

### Enfoque Programático

Para más control, puede usar d-back en su código Python:

```python
import asyncio
from d_back.server import WebSocketServer

async def main():
    # Create server instance
    server = WebSocketServer(port=3000, host="localhost")
    
    # Optional: Set up custom callbacks
    # server.on_get_user_data(my_user_data_callback)
    # server.on_get_server_data(my_server_data_callback)
    
    # Start the server
    print("Starting d-back server...")
    await server.start()

# Run the server
asyncio.run(main())
```

Cada paso explicado:
1. **Importar módulos**: Importe asyncio para ejecución asíncrona y la clase WebSocketServer
2. **Crear servidor**: Instancie WebSocketServer con el puerto y host deseados
3. **Configurar callbacks** (opcional): Personalice fuentes de datos con funciones callback
4. **Iniciar servidor**: Llame `await server.start()` para comenzar a aceptar conexiones

## Su Primera Conexión WebSocket

Una vez que el servidor esté ejecutándose, puede probar la conexión WebSocket desde un cliente.

### Usando JavaScript/Navegador

Abra la consola de su navegador y ejecute:

```javascript
// Connect to d-back
const socket = new WebSocket('ws://localhost:3000');

socket.onopen = () => {
    console.log('Connected to d-back!');
    // Request user data for a mock server
    socket.send(JSON.stringify({
        type: 'get_user_data',
        serverId: '232769614004748288'
    }));
};

socket.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log('Received:', data);
};
```

**Formato del Mensaje**: La solicitud `get_user_data` incluye:
- `type`: Tipo de mensaje (`"get_user_data"`)
- `serverId`: ID del servidor de Discord (formato snowflake)

**Respuesta Esperada**: Recibirá un objeto JSON que contiene datos de usuario:
```json
{
  "type": "user_data",
  "serverId": "232769614004748288",
  "users": {
    "user123": {
      "uid": "user123",
      "username": "ExampleUser",
      "status": "online",
      "roleColor": "#ff6b6b"
    }
  }
}
```

### Usando la Biblioteca websockets de Python

También puede conectarse usando la biblioteca `websockets` de Python:

```python
import asyncio
import json
import websockets

async def test_connection():
    uri = "ws://localhost:3000"
    async with websockets.connect(uri) as websocket:
        print("Connected to d-back!")
        
        # Request user data
        request = {
            "type": "get_user_data",
            "serverId": "232769614004748288"
        }
        await websocket.send(json.dumps(request))
        
        # Receive response
        response = await websocket.recv()
        data = json.loads(response)
        print("Received:", data)

asyncio.run(test_connection())
```

### Comportamiento Esperado

Cuando se conecte exitosamente, debería ver:
1. **Conexión establecida**: WebSocket se abre exitosamente
2. **Lista de servidores recibida**: Mensaje inicial con servidores de Discord disponibles
3. **Datos de usuario devueltos**: Respuesta con presencia de usuario simulada e información de roles

## Comprender los Datos Simulados

d-back viene con servidores de Discord simulados preconfigurados para desarrollo y pruebas. ¡Esto significa que puede comenzar a construir y probar inmediatamente sin configurar credenciales de la API de Discord!

Los servidores simulados disponibles son:

- **servidor d-world** (`232769614004748288`): Servidor de desarrollo principal con 4 usuarios activos en diferentes estados
- **servidor docs** (`482241773318701056`): Servidor de documentación con 1 usuario
- **servidor oauth2** (`123456789012345678`): Servidor protegido para probar flujos de autenticación OAuth2 con 1 usuario
- **servidor my repos** (`987654321098765432`): Servidor de exhibición de repositorios con 21 usuarios

!!! tip "Perfecto para Desarrollo"
    Los datos simulados son ideales para:
    
    - Desarrollo de frontend sin dependencias de backend
    - Probar visualización d-zone con datos realistas
    - Demostrar el sistema sin claves de API de Discord
    - Pipelines CI/CD y pruebas automatizadas

Para usar datos reales de Discord en producción, necesitará implementar proveedores de datos personalizados. Consulte la guía [Proveedores de Datos Personalizados](user-guide/custom-data-providers.md) para obtener detalles.

## Próximos Pasos

¡Felicitaciones! Ahora tiene d-back en funcionamiento. Aquí está lo que debe explorar a continuación:

- **[Guía del Usuario](user-guide/index.md)**: Aprenda sobre opciones de configuración, callbacks y personalización
- **[Configuración](user-guide/configuration.md)**: Personalice configuraciones del servidor, puertos y servicio de archivos estáticos
- **[Callbacks y Personalización](user-guide/callbacks.md)**: Reemplace datos simulados con sus propias fuentes de datos
- **[Proveedores de Datos Personalizados](user-guide/custom-data-providers.md)**: Integre con la API de Discord o bases de datos
- **[Referencia de API](api-reference.md)**: Documentación detallada de todas las clases y métodos
- **[Guía del Desarrollador](developer-guide.md)**: Directrices de contribución y descripción general de la arquitectura

!!! question "¿Necesita Ayuda?"
    Si encuentra problemas, consulte los [GitHub Issues](https://github.com/NNTin/d-back/issues) o inicie una [Discusión](https://github.com/NNTin/d-back/discussions).
