#!/usr/bin/env python3
import pandas as pd
from fastapi.responses import HTMLResponse, JSONResponse
from core.settings import Settings
from processors.cep_processor import CEPProcessor


class RouteProcessor:
     async def execute(
        self
    ) -> dict:

        try:
            # Verifica se o arquivo CSV existe
            if not Settings.CSV_INPUT.exists():
                return JSONResponse(
                    status_code=404,
                    content={"error": f"Arquivo {Settings.CSV_INPUT} não encontrado"}
                )
            
            # Tenta ler o CSV - detecta automaticamente se tem header
            # Se a primeira linha parecer um CEP, não é header
            first_line = pd.read_csv(Settings.CSV_INPUT, nrows=1, header=None).iloc[0, 0]
            has_header = not str(first_line).replace('-', '').isdigit()
            
            if has_header:
                df = pd.read_csv(Settings.CSV_INPUT)
            else:
                # CSV sem header - todas as linhas são dados
                df = pd.read_csv(Settings.CSV_INPUT, header=None)
            
            # Detecta coluna de CEP
            cep_column = None
            
            # Caso 1: CSV com header nomeado
            for col in df.columns:
                if 'cep' in str(col).lower() or 'zip' in str(col).lower():
                    cep_column = col
                    break
            
            # Caso 2: CSV sem header ou header numérico (0, 1, 2...)
            if cep_column is None:
                # Se a primeira coluna é numérica (0, 1, etc) ou não tem nome claro
                # Assume que é um CSV sem header e usa a primeira coluna
                if len(df.columns) > 0:
                    cep_column = df.columns[0]
                    print(f"Header não identificado. Usando primeira coluna: '{cep_column}'")
            
            if cep_column is None:
                return JSONResponse(
                    status_code=400,
                    content={"error": "CSV vazio ou sem colunas"}
                )
            
            # Remove valores nulos e converte para string
            ceps = df[cep_column].dropna().astype(str).str.replace('-', '').tolist()
            
            # Processa
            processor = CEPProcessor()
            await processor.process(ceps)
            
            # Retorna estatísticas e preview dos dados
            preview_results = processor.results[:10] if len(processor.results) > 10 else processor.results
            preview_errors = processor.errors[:10] if len(processor.errors) > 10 else processor.errors
            
            return {
                "success": True,
                "stats": processor.stats,
                "preview_results": preview_results,
                "preview_errors": preview_errors,
                "files": {
                    "json": str(Settings.JSON_OUTPUT.name),
                    "xml": str(Settings.XML_OUTPUT.name),
                    "errors_csv": str(Settings.CSV_ERRORS.name) if processor.errors else None
                }
            }
            
        except Exception as e:
            return JSONResponse(
                status_code=500,
                content={"error": str(e)}
            )    
