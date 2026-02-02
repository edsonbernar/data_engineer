# Sistema de Processamento de CEPs

Sistema profissional de processamento paralelo de CEPs usando ViaCEP API, desenvolvido com **FastAPI**, **aiohttp** e **Pandas**.

## Características

- **Processamento paralelo** com até 50 requisições simultâneas
- **Retry automático** com backoff exponencial
- **Persistência em SQLite** com suporte a JSON
- **Múltiplos formatos de saída**: JSON, XML e CSV
- **Interface web moderna** com FastAPI + Jinja2
- **Modo CLI** para execução via linha de comando
- **CSS responsivo** para visualização profissional dos dados

## Instalação

```bash
# Instalar dependências
pip install -r requirements.txt --break-system-packages
```

## Modos de Uso

### Modo Interface Web (Recomendado)

```bash
# Iniciar servidor
python app.py

# Acessar no navegador
# http://localhost:8000
```

**Funcionalidades da interface:**
- Botão "Processar CEPs" para iniciar o processamento
- Visualização em tempo real das estatísticas
- Preview das tabelas de resultados e erros
- Download dos arquivos gerados

### Modo CLI (Linha de Comando)

```bash
# Executar processamento via CLI
python app.py --cli
```

## Estrutura de Arquivos

```
cep_project/
├── core
│   └── data_base.py          # SQLite (rotina data base creation)
│   └── settings.py           # File settings
│   └── zip_code_data.csv     # CSV de entrada - fonte de CEPs
├── out_put
│   └── cep.db                # SQLite (criado automaticamente)
│   └── enderecos.json        # Saída JSON
│   └── enderecos.xml         # Saída XML
│   └── errors.csv            # Erros (se houver)
├── processors
│   └── cep_processor.py      # Processador principal cep
│   └── cli_cep_processor.py  # Chamada consolo
│   └── route_processor.py    # Classe processor rota cep
├── templates/
│   └── index.html            # Template HTML
├── static/
│   └── style.css             # Estilos CSS
├── requirements.txt          # Dependências Python
├── Dockerfile                # Dockerfile
├── setup.sh                  # file run
├── app.py                    # Aplicação principal
```

## Banco de Dados SQLite

O sistema cria automaticamente duas tabelas:

### Tabela `results`
```sql
CREATE TABLE results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cep TEXT UNIQUE NOT NULL,
    data JSON NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

### Tabela `errors`
```sql
CREATE TABLE errors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cep TEXT NOT NULL,
    error_message TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

## Formatos de Saída

### 1. JSON (`enderecos.json`)
```json
[
  {
    "cep": "01310-100",
    "logradouro": "Avenida Paulista",
    "bairro": "Bela Vista",
    "localidade": "São Paulo",
    "uf": "SP",
    "estado": "São Paulo",
    "regiao": "Sudeste",
    "ibge": "3550308",
    "ddd": "11"
  }
]
```

### 2. XML (`enderecos.xml`)
```xml
<enderecos>
  <endereco>
    <cep>01310-100</cep>
    <logradouro>Avenida Paulista</logradouro>
    <bairro>Bela Vista</bairro>
    <localidade>São Paulo</localidade>
    <uf>SP</uf>
    <estado>São Paulo</estado>
    <regiao>Sudeste</regiao>
  </endereco>
</enderecos>
```

### 3. CSV de Erros (`errors.csv`)
```csv
cep,error,timestamp
12345-678,CEP não encontrado na base ViaCEP,2026-01-30T00:00:00
```

## Configurações

Você pode ajustar estas constantes no `app.py`:

```python
MAX_CONCURRENT_REQUESTS = 5   # Requisições simultâneas
REQUEST_TIMEOUT = 10          # Timeout em segundos
MAX_RETRIES = 2               # Tentativas em caso de erro
```

## Interface Web

A interface possui:
- **Card de processamento** com botão de ação
- **Estatísticas em tempo real**: total, sucessos, erros, taxa de sucesso, tempo, velocidade
- **Lista de arquivos gerados** com badges coloridos
- **Tabelas de preview**: 10 primeiros resultados e erros
- **Design responsivo** que funciona em desktop e mobile

## API Endpoints

### `GET /`
Retorna a página HTML principal

### `POST /process`
Processa todos os CEPs do arquivo CSV

**Resposta:**
```json
{
  "success": true,
  "stats": {
    "total": 30,
    "success": 28,
    "errors": 2,
    "start_time": 1738195200.0,
    "end_time": 1738195210.5
  },
  "preview_results": [...],
  "preview_errors": [...],
  "files": {
    "json": "enderecos.json",
    "xml": "enderecos.xml",
    "errors_csv": "errors.csv"
  }
}
```

## Performance

Com 50 requisições simultâneas, o sistema consegue processar:
- **~150-200 CEPs por segundo** (dependendo da rede)
- **10.000 CEPs em ~50-70 segundos**

## Tratamento de Erros

O sistema trata elegantemente:
- CEPs não encontrados na base ViaCEP
- Timeouts de requisição
- Erros de rede
- CEPs inválidos
- Limitação de taxa (rate limiting)

Todos os erros são:
1. Registrados na tabela `errors` do SQLite
2. Salvos no arquivo `errors.csv`
3. Exibidos na interface web

## Tecnologias Utilizadas

- **FastAPI**: Framework web assíncrono de alta performance
- **aiohttp**: Cliente HTTP assíncrono para requisições paralelas
- **Pandas**: Manipulação eficiente de dados
- **SQLite**: Banco de dados embutido com suporte JSON
- **Jinja2**: Engine de templates para HTML
- **Uvicorn**: Servidor ASGI de alta performance

## Exemplo de Uso no CSV

Seu arquivo `zip_code_data.csv` deve ter o seguinte formato:

```csv
cep
01310-100
20040-020
30130-100
```

Ou também aceita outras variações de nome de coluna:
- `cep`
- `CEP`
- `zip_code`
- `zipcode`

## Diferenciais Técnicos

1. **Processamento Paralelo**: Usa `asyncio` + `aiohttp.ClientSession` para requisições simultâneas
2. **Semáforo Inteligente**: Controla o número máximo de requisições paralelas
3. **Retry com Backoff**: Tenta novamente em caso de falhas temporárias
4. **Connection Pooling**: Reutiliza conexões HTTP para melhor performance
5. **Batch Processing**: Processa CEPs em lotes de 1000 para melhor controle
6. **JSON no SQLite**: Usa a extensão JSON1 do SQLite para armazenamento eficiente

## Suporte

Para dúvidas ou problemas, verifique:
- Logs no console
- Arquivo `errors.csv`
- Tabela `errors` no SQLite

---

Desenvolvido usando as melhores práticas de Python e engenharia de software.
