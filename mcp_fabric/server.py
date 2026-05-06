import asyncio
import logging
import subprocess
import mcp.server.stdio
from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
import mcp.types as types

# 1. Configuración de Logs profesional
# Crítico: Los logs van a un archivo para no ensuciar el canal stdio (reservado para JSON-RPC).
logging.basicConfig(
    filename='mcp_fabric.log',
    level=logging.DEBUG, 
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# 2. Inicialización del servidor
server = Server("mcp-fabric")

# --- ZONA DE HERRAMIENTAS (INTERFACE) ---

@server.list_tools()
async def handle_list_tools() -> types.ListToolsResult:
    """Registra las herramientas disponibles. Esto es lo que el LLM 'lee' para saber qué puede hacer."""
    logging.info("El cliente solicitó la lista de herramientas.")
    return types.ListToolsResult(
        tools=[
            types.Tool(
                name="run_fabric_pattern",
                description="Ejecuta un patrón de Fabric (ej. extract_wisdom, summarize) sobre un texto.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "pattern_name": {
                            "type": "string",
                            "description": "El nombre del patrón de Fabric que quieres usar."
                        },
                        "input_text": {
                            "type": "string",
                            "description": "El texto que será procesado por el patrón."
                        }
                    },
                    "required": ["pattern_name", "input_text"]
                }
            )
        ]
    )

@server.call_tool()
async def handle_call_tool(name: str, arguments: dict | None) -> types.CallToolResult:
    """Lógica de ejecución: Aquí es donde conectamos con el binario de Fabric."""
    logging.info(f"Llamada a herramienta: {name} con argumentos: {arguments}")
    
    if name == "run_fabric_pattern":
        if not arguments or "pattern_name" not in arguments or "input_text" not in arguments:
             return types.CallToolResult(
                isError=True,
                content=[types.TextContent(type="text", text="Error: Faltan argumentos requeridos.")]
            )
            
        pattern = arguments["pattern_name"]
        text = arguments["input_text"]
        
        # --- EJECUCIÓN REAL DE FABRIC CLI ---
        try:
            logging.info(f"Lanzando proceso: fabric --pattern {pattern}")
            
            # Ejecutamos fabric pasándole el texto por el stdin (tubería)
            process = subprocess.run(
                ["fabric", "--pattern", pattern],
                input=text,
                capture_output=True,
                text=True,
                check=True,
                encoding='utf-8' # Crucial para evitar errores de caracteres en Windows
            )
            
            return types.CallToolResult(
                content=[types.TextContent(type="text", text=process.stdout)]
            )

        except subprocess.CalledProcessError as e:
            # Fabric devolvió un error (ej. el patrón no existe)
            error_msg = f"Error de Fabric (Exit Code {e.returncode}): {e.stderr}"
            logging.error(error_msg)
            return types.CallToolResult(
                isError=True,
                content=[types.TextContent(type="text", text=error_msg)]
            )
        except FileNotFoundError:
            # No se encuentra el comando 'fabric' en el sistema
            error_msg = "Error: El comando 'fabric' no está instalado o no se encuentra en el PATH."
            logging.error(error_msg)
            return types.CallToolResult(
                isError=True,
                content=[types.TextContent(type="text", text=error_msg)]
            )
        except Exception as e:
            # Cualquier otro error inesperado
            logging.error(f"Error inesperado: {str(e)}")
            return types.CallToolResult(
                isError=True,
                content=[types.TextContent(type="text", text=f"Error interno: {str(e)}")]
            )

    return types.CallToolResult(
        isError=True,
        content=[types.TextContent(type="text", text=f"Herramienta desconocida: {name}")]
    )

# --- ZONA DE TRANSPORTE (EL MOTOR) ---

async def main():
    logging.info("Iniciando servidor MCP Fabric...")
    
    # Configuración de notificaciones requerida por el SDK para evitar errores de NoneType
    opciones_notificacion = NotificationOptions(
        prompts_changed=False,
        resources_changed=False,
        tools_changed=False
    )

    options = InitializationOptions(
        server_name="mcp-fabric",
        server_version="0.1.0",
        capabilities=server.get_capabilities(
            notification_options=opciones_notificacion,
            experimental_capabilities={},
        )
    )

    # Conectamos la entrada y salida estándar al servidor MCP
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, options)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Servidor detenido por el usuario.")




