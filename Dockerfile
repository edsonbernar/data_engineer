# Dockerfile para Sistema de Processamento de CEPs
# Python 3.11 slim (imagem leve)
FROM python:3.11-slim

# Metadata
LABEL maintainer="Sistema CEP"
LABEL description="Sistema de Processamento de CEPs com FastAPI"

# Variáveis de ambiente
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Diretório de trabalho
WORKDIR /app

# Instala dependências do sistema (se necessário)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copia arquivo de dependências
COPY requirements.txt .

# Instala dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Copia código da aplicação
COPY . .

# Cria diretórios necessários
RUN mkdir -p /app/data /app/outputs

# Expõe porta da aplicação
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/')" || exit 1

# Comando padrão (servidor FastAPI)
CMD ["python", "app.py"]

# Para rodar em modo CLI, use:
# docker run <image> python app.py --cli
