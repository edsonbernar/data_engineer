#!/usr/bin/env python3
"""
Sistema de Processamento de CEPs - FastAPI + CLI
Processa CEPs em paralelo usando ViaCEP API
"""
import asyncio
import os
import sys
import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from core.settings import Settings
from processors.route_processor import RouteProcessor
from processors.cli_cep_processor import run_cli



app = FastAPI(title="Sistema de Processamento de CEPs")


app.mount(
    "/static", 
    StaticFiles(directory=str(os.path.join(Settings.BASE_DIR, "static"))), 
    name="static"
)

templates = Settings.TEMPLATES


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Página inicial"""
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/process")
async def process_ceps():
    """Endpoint para processar CEPs"""
    return await RouteProcessor().execute()
    


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--cli":
        # Modo CLI
        asyncio.run(run_cli())
    else:
        # Modo servidor FastAPI
        print("\nIniciando servidor FastAPI...")
        print(f"Acesse: http://localhost:8000")
        print(f"Documentação: http://localhost:8000/docs\n")
        uvicorn.run(app, host="0.0.0.0", port=8000)
