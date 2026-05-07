# MCP Fabric Server

Servidor MCP (Model Context Protocol) que expone los patrones de **Fabric AI** como herramientas accesibles para LLMs como Claude Desktop, CrewAI u otros clientes compatibles con MCP.

Permite que un modelo de IA ejecute patrones como `summarize`, `extract_wisdom`, `rewrite`, `improve_writing`, etc., directamente desde una conversación o un agente autónomo.

---

## 🚀 Características

- Transporte **stdio** compatible con MCP.
- Arquitectura **asíncrona** basada en `asyncio`.
- Herramienta principal:
  - `run_fabric_pattern`: ejecuta cualquier patrón de Fabric sobre un texto.
- Logging profesional (`mcp_fabric.log`) sin contaminar el canal JSON-RPC.
- Integración lista para:
  - Claude Desktop
  - CrewAI
  - MCP Inspector
  - Cualquier cliente MCP

---

## 📦 Requisitos

- Python 3.10+
- Fabric AI instalado en el sistema (Go)
- OpenAI API Key configurada en Fabric (`fabric --setup`)
- `pip` actualizado

---

## 📥 Instalación

Instalación local:

```bash
pip install .

