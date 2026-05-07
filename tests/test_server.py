import pytest
from unittest.mock import patch, MagicMock
import mcp.types as types
# Importamos la función desde tu archivo server.py
from mcp_fabric.server import handle_call_tool

@pytest.mark.asyncio
async def test_run_fabric_pattern_success():
    """Prueba que el servidor gestiona correctamente la llamada a Fabric."""
    
    # Configuramos el simulador del proceso externo
    mock_process = MagicMock()
    mock_process.stdout = "Sabiduría extraída: El conocimiento es poder."
    mock_process.returncode = 0

    # Interceptamos subprocess.run para que NO ejecute nada real
    with patch("subprocess.run", return_value=mock_process) as mock_run:
        
        arguments = {
            "pattern_name": "extract_wisdom",
            "input_text": "Texto de prueba para el CI"
        }
        
        # Ejecutamos la lógica de tu servidor
        result = await handle_call_tool("run_fabric_pattern", arguments)

        # Verificaciones estratégicas
        assert isinstance(result, types.CallToolResult)
        assert "Sabiduría extraída" in result.content[0].text
        
        # Verificamos que se intentó llamar al comando correcto
        # Nota: Aquí usamos "fab" porque es lo que tienes en tu script
        mock_run.assert_called_once()
        args, kwargs = mock_run.call_args
        assert args[0] == ["fab", "--pattern", "extract_wisdom"]