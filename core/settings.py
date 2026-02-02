import os
import sys
from pathlib import Path
from fastapi.templating import Jinja2Templates


class Settings:
    """Application settings"""

    debug: bool
    project_name: str
    version: str
    description: str

    """Database settings"""

    # Configurações

    BASE_DIR = Path(os.path.dirname(os.path.abspath(__file__))).parent
    CSV_INPUT: str = BASE_DIR / "core" / "zip_code_data.csv"
    DB_PATH: str = BASE_DIR / "out_put" / "cep.db"
    CSV_ERRORS: str = BASE_DIR / "out_put" / "errors.csv"
    JSON_OUTPUT: str = BASE_DIR / "out_put" / "enderecos.json"
    XML_OUTPUT: str = BASE_DIR / "out_put" / "enderecos.xml"

    MAX_CONCURRENT_REQUESTS: int = 50  # Limite de requisições simultâneas
    REQUEST_TIMEOUT: int = 10  # Timeout em segundos
    MAX_RETRIES: int = 2  # Número máximo de tentativas
    # O ViaCEP é uma API pública com rate limit de ~300 req/mi
    SERVICE_CEP: str = "https://viacep.com.br/ws/{cep}/json/"
    #SERVICE_CEP: str = "https://brasilapi.com.br/api/cep/v1/{cep}"


    TEMPLATES: Jinja2Templates = Jinja2Templates(directory=str(os.path.join(BASE_DIR, "templates")))

    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


