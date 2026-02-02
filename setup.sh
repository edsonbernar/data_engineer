#!/bin/bash

echo "======================================================"
echo "  Sistema de Processamento de CEPs - Setup"
echo "======================================================"
echo ""

# Cores para output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}1. Instalando dependências...${NC}"
pip install -r requirements.txt --break-system-packages

if [ $? -eq 0 ]; then
    echo -e "${GREEN} Dependências instaladas com sucesso${NC}"
else
    echo -e "${YELLOW} Erro ao instalar dependências. Verifique sua conexão.${NC}"
    exit 1
fi

echo ""
echo -e "${BLUE}2. Verificando arquivos...${NC}"

if [ -f "zip_code_data.csv" ]; then
    echo -e "${GREEN}Arquivo zip_code_data.csv encontrado${NC}"
else
    echo -e "${YELLOW}Arquivo zip_code_data.csv não encontrado${NC}"
    echo "   Crie um arquivo CSV com uma coluna 'cep' contendo seus CEPs"
fi

echo ""
echo -e "${GREEN}======================================================"
echo "  Setup concluído!"
echo "======================================================${NC}"
echo ""
echo "Para executar o sistema, escolha um modo:"
echo ""
echo -e "${BLUE}Modo Interface Web (Recomendado):${NC}"
echo "  python app.py"
echo "  Depois acesse: http://localhost:7750"
echo ""
echo -e "${BLUE}Modo CLI:${NC}"
echo "  python app.py --cli"
echo ""
