import sqlite3

DATABASE = "flutuar.db" # nome do arquivo

def get_connection(): # conexão com o BD
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row 
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS alunos ("
        "id INTEGER PRIMARY KEY AUTOINCREMENT,"
        "nome TEXT NOT NULL,"
        "telefone TEXT NOT NULL,"
        "email TEXT NOT NULL UNIQUE,"
        "curso TEXT NOT NULL,"
        "nivel_ippi TEXT,"
        "observacoes TEXT,"
        "data_cadastro TEXT NOT NULL"
        ")"
    )
    conn.commit()
    conn.close()