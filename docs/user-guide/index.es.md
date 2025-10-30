# Guía del Usuario

¡Bienvenido a la guía del usuario de d-back! Esta guía integral cubre todo lo que necesita para usar efectivamente d-back como servidor WebSocket para su simulación de vida ambiental d-zone u otras aplicaciones en tiempo real.

## Introducción

Esta guía está diseñada para usuarios que ya han completado el tutorial de [Primeros Pasos](../getting-started.md) y desean profundizar en las características y capacidades de d-back. Ya sea que esté buscando personalizar el comportamiento del servidor, integrar con datos reales de Discord u optimizar su configuración, encontrará la información que necesita aquí.

La guía del usuario está organizada en tres áreas principales:

- **Configuración**: Aprenda cómo configurar d-back a través de opciones de línea de comandos, variables de entorno y configuraciones programáticas
- **Callbacks y Personalización**: Descubra cómo personalizar el comportamiento del servidor usando funciones callback para recuperación de datos, autenticación y más
- **Proveedores de Datos Personalizados**: Reemplace datos simulados con integración real de la API de Discord o sus propias fuentes de datos personalizadas

## Estructura de la Guía

<div class="grid cards" markdown>

-   :material-cog:{ .lg .middle } **Configuración**

    ---

    Aprenda sobre opciones de línea de comandos, variables de entorno y configuraciones del servidor

    [:octicons-arrow-right-24: Guía de Configuración](configuration.md)

-   :material-code-braces:{ .lg .middle } **Callbacks y Personalización**

    ---

    Personalice el comportamiento del servidor con funciones callback para recuperación de datos y autenticación

    [:octicons-arrow-right-24: Guía de Callbacks](callbacks.md)

-   :material-database:{ .lg .middle } **Proveedores de Datos Personalizados**

    ---

    Reemplace datos simulados con integración real de la API de Discord o fuentes de datos personalizadas

    [:octicons-arrow-right-24: Guía de Proveedores de Datos](custom-data-providers.md)

</div>

## Casos de Uso Comunes

¿Necesita lograr una tarea específica? Aquí hay enlaces rápidos a escenarios comunes:

| Escenario | Dónde Buscar |
|----------|---------------|
| Quiero cambiar el puerto del servidor | [Configuración → Opciones de Línea de Comandos](configuration.md#command-line-options) |
| Quiero servir mis propios archivos estáticos | [Configuración → Servicio de Archivos Estáticos](configuration.md#static-file-serving) |
| Quiero usar datos reales de Discord | [Proveedores de Datos Personalizados](custom-data-providers.md) |
| Quiero agregar autenticación OAuth2 | [Callbacks → Validación OAuth2](callbacks.md#on_validate_discord_user-callback) |
| Quiero transmitir mensajes personalizados | [Callbacks → Métodos de Difusión](callbacks.md#broadcasting-methods) |
| Quiero personalizar el formato de datos de usuario | [Callbacks → Callback de Datos de Usuario](callbacks.md#on_get_user_data-callback) |

## Referencia Rápida

Aquí hay un resumen de conceptos clave que encontrará en esta guía:

| Concepto | Descripción |
|---------|-------------|
| **WebSocketServer** | Clase principal del servidor que maneja conexiones WebSocket, solicitudes HTTP y difusión de mensajes |
| **MockDataProvider** | Generador de datos de prueba integrado que simula actividad de usuario de Discord |
| **Callbacks** | Ganchos de personalización que permiten anular el comportamiento predeterminado (p. ej., `on_get_user_data`, `on_get_server_data`) |
| **Servicio de Archivos Estáticos** | Servidor HTTP integrado para entregar activos de frontend como HTML, CSS y JavaScript |
| **Difusión** | Métodos para enviar actualizaciones en tiempo real a clientes conectados (presencia, mensajes, etc.) |
| **Integración OAuth2** | Soporte para autenticación OAuth2 de Discord y validación de tokens |

!!! tip "¿Necesita Detalles de la API?"
    Para documentación detallada de la API incluyendo firmas de métodos, parámetros y tipos de retorno, consulte la [Referencia de API](../api-reference.md).

## ¿Qué Sigue?

¿Listo para personalizar su configuración de d-back? Comience con:

1. **[Configuración](configuration.md)** - Configure su servidor con las configuraciones correctas
2. **[Callbacks y Personalización](callbacks.md)** - Aprenda cómo personalizar el comportamiento
3. **[Proveedores de Datos Personalizados](custom-data-providers.md)** - Integre fuentes de datos reales

!!! question "¿Preguntas?"
    Si no puede encontrar lo que está buscando, consulte la [Referencia de API](../api-reference.md) o visite nuestras [GitHub Discussions](https://github.com/NNTin/d-back/discussions).
