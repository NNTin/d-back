# Documentación de d-back

**Servidor WebSocket para integración de Discord con simulación de vida ambiental d-zone**

Bienvenido a la documentación oficial de **d-back** – el servicio backend inteligente que impulsa la mágica simulación de vida ambiental **d-zone**. d-back sirve como puente en tiempo real entre servidores de Discord y el hermoso frontend d-zone, creando una experiencia inmersiva donde cada usuario de Discord se convierte en parte de un ecosistema digital vivo y respirable.

d-zone es una simulación de vida ambiental donde la presencia y actividad de los usuarios en un servidor de Discord influyen sutilmente en un entorno digital vivo. ¡Piense en ello como un terrario digital que reacciona a la energía de su comunidad! d-back proporciona datos de usuario en tiempo real a través de conexiones WebSocket, haciendo posible esta integración fluida.

---

## Enlaces Rápidos

<div class="grid cards" markdown>

-   :material-rocket-launch:{ .lg .middle } __Primeros Pasos__

    ---

    Instale y ejecute su primer servidor WebSocket en minutos

    [:octicons-arrow-right-24: Comenzar](getting-started.md)

-   :material-book-open-variant:{ .lg .middle } __Guía del Usuario__

    ---

    Aprenda cómo configurar y personalizar d-back para sus necesidades

    [:octicons-arrow-right-24: Guía del Usuario](user-guide/index.md)

-   :material-code-braces:{ .lg .middle } __Referencia de API__

    ---

    Explore la documentación completa de la API con ejemplos detallados

    [:octicons-arrow-right-24: Referencia de API](api-reference.md)

-   :material-hammer-wrench:{ .lg .middle } __Guía del Desarrollador__

    ---

    Contribuya al proyecto y extienda su funcionalidad

    [:octicons-arrow-right-24: Guía del Desarrollador](developer-guide.md)

</div>

---

## Características Clave

!!! success "Servidor WebSocket"
    Comunicación bidireccional en tiempo real con el frontend d-zone, soportando múltiples conexiones concurrentes y difusión eficiente de mensajes.

!!! success "Simulación de Actividad de Usuario"
    Datos simulados sofisticados de usuarios de Discord con estados de presencia realistas (en línea, inactivo, DND, desconectado) perfectos para desarrollo y pruebas.

!!! success "Soporte Multi-Servidor"
    Maneje múltiples servidores de Discord simultáneamente, cada uno con sus propias listas de usuarios y configuraciones.

!!! success "OAuth2 Listo"
    Soporte integrado para autenticación OAuth2 de Discord, permitiendo validación segura de usuarios y control de acceso al servidor.

!!! success "Servicio de Archivos Estáticos"
    Sirva activos del frontend directamente desde el backend (websockets 10.0+), simplificando el despliegue y el alojamiento.

---

## Ejemplo Rápido

Comience con d-back en solo unas pocas líneas de código:

```python
import asyncio
from d_back.server import WebSocketServer

async def main():
    # Create server instance
    server = WebSocketServer(port=3000, host="localhost")
    
    # Optional: Set up custom callbacks
    server.on_get_user_data(my_user_data_callback)
    server.on_get_server_data(my_server_data_callback)
    
    # Start the server
    print("Starting d-back server...")
    await server.start()

# Run the server
asyncio.run(main())
```

O use la interfaz de línea de comandos:

```bash
# Start with default settings
python -m d_back

# Custom configuration
python -m d_back --port 8080 --host 0.0.0.0 --static-dir ./my-frontend
```

---

## Información del Proyecto

![Last Commit](https://img.shields.io/github/last-commit/NNTin/d-back)
![Build Status](https://github.com/NNTin/d-back/actions/workflows/test.yml/badge.svg)
![PyPI](https://img.shields.io/pypi/v/d-back)
![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-blue.svg)

**Repositorio:** [NNTin/d-back](https://github.com/NNTin/d-back) en GitHub  
**Paquete:** [d-back](https://pypi.org/project/d-back/) en PyPI  
**Licencia:** Licencia MIT  
**Python:** 3.8 o superior

---

## Próximos Pasos

¿Listo para sumergirse? Aquí está lo que debe explorar a continuación:

1. **[Primeros Pasos](getting-started.md)** - Instale d-back y ejecute su primer servidor
2. **Capacidades de Datos Simulados** - Aprenda sobre el sistema integral de datos simulados para pruebas sin acceso a la API de Discord
3. **[Frontend d-zone](https://nntin.github.io/d-zone/)** - Explore el hermoso frontend que da vida a su comunidad de Discord
4. **Documentación de API** - Descubra todos los ganchos de callback y opciones de personalización

!!! tip "Listo para Desarrollo"
    d-back viene con servidores de Discord simulados preconfigurados y datos de usuario realistas, haciéndolo perfecto para desarrollo, pruebas y propósitos de demostración. ¡No se requieren claves de API de Discord para comenzar!

---

<p align="center">
  <em>Construido con ❤️ para el ecosistema d-world</em>
</p>
