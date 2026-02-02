#!/usr/bin/env python3

import sys
import pandas as pd
from core.settings import Settings
from processors.cep_processor import CEPProcessor


async def run_cli():
    """Executa o processamento via linha de comando"""
    print("\nSistema de Processamento de CEPs - Modo CLI\n")
    
    # Verifica se o arquivo CSV existe
    if not Settings.CSV_INPUT.exists():
        print(f"Erro: Arquivo {Settings.CSV_INPUT} não encontrado")
        sys.exit(1)
    
    # Lê o CSV - detecta automaticamente se tem header
    print(f"Lendo arquivo: {Settings.CSV_INPUT}")
    
    # Verifica se a primeira linha parece um CEP (sem header)
    first_line = pd.read_csv(Settings.CSV_INPUT, nrows=1, header=None).iloc[0, 0]
    has_header = not str(first_line).replace('-', '').isdigit()
    
    if has_header:
        df = pd.read_csv(Settings.CSV_INPUT)
        print(f"CSV com header detectado")
    else:
        # CSV sem header - todas as linhas são dados
        df = pd.read_csv(Settings.CSV_INPUT, header=None)
        print(f"CSV sem header - usando todas as {len(df)} linhas")
    
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
        print("Erro: CSV vazio ou sem colunas")
        sys.exit(1)
    
    print(f"Coluna de CEP: '{cep_column}'")
    
    # Processa CEPs
    ceps = df[cep_column].dropna().astype(str).str.replace('-', '').tolist()
    
    processor = CEPProcessor()
    await processor.process(ceps)
    
    print("\nProcessamento concluído com sucesso!")

