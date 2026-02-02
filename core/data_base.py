import sqlite3
from core.settings import Settings


def init_database():
    """Inicializa o banco de dados SQLite com suporte a JSON"""
    conn = sqlite3.connect(Settings.DB_PATH)
    cursor = conn.cursor()
    
    # Tabela de resultados com campo JSON
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cep TEXT UNIQUE NOT NULL,
            data JSON NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Tabela de erros
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS errors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cep TEXT NOT NULL,
            error_message TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()
    print(f"Banco de dados inicializado: {Settings.DB_PATH}")