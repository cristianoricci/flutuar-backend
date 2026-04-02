from flask import Flask, request, jsonify
from flask_cors import CORS
from flasgger import Swagger
from database import init_db, get_connection
from datetime import datetime


# Inicialização da aplicação Flask
app = Flask(__name__)

# Configurção de CORS: Permite que frontends em outros dominios acessem a API
CORS(app)

# Configurção customizada do Swagger para a documentação automática da API
swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": "apispec",
            "route": "/apispec.json",
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True,
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/apidocs",
}
Swagger(app)

# Regras de Negócio: Definição de domínios aceitos pelo sistema
CURSOS_VALIDOS = ["Iniciante", "Cross", "Voo Duplo"]
NIVEIS_IPPI = ["1", "2", "3", "4"]

@app.route("/cadastrar_aluno",  methods = ["POST"])
def cadastrar_aluno():
    """
   Cadastra um novo aluno.
    ---
    tags:
      - Alunos
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - nome
            - telefone
            - email
            - curso
          properties:
            nome:
              type: string
              example: "João Silva"
            telefone:
              type: string
              example: "35999998888"
            email:
              type: string
              example: "joao@email.com"
            curso:
              type: string
              example: "Iniciante"
            nivel_ippi:
              type: string
              example: "1"
            observacoes:
              type: string
              example: "Disponível aos fins de semana"
    responses:
      201:
        description: Aluno cadastrado com sucesso
      400:
        description: Dados inválidos
    """
    # 1. Captura e limpeza inicial dos dados recebidos via JSON
    dados = request.get_json()

    # 2. Validação de campos obrigatórios: impede strings vazias no banco
    for campo in ["nome", "telefone", "email", "curso"]:
        if not dados.get(campo, "").strip():
            return jsonify({"erro": f"Campo obrigatório ausente: {campo}"}), 400
        
    # 3. Verificação de integridade: garante que o curso e nivel IPPI sejam válidos        
    if dados["curso"] not in CURSOS_VALIDOS:
            return jsonify({"erro": "Curso invalido.", "cursos_validos": CURSOS_VALIDOS})
        
    if dados.get("nivel_ippi") and dados["nivel_ippi"] not in NIVEIS_IPPI:
            return jsonify({"erro": "Nível IPPI inválido.", "niveis_validos": NIVEIS_IPPI})

    # Registro do timestamp no momento da criação 
    data_cadastro = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 4. Camada de persistência: Inserção no SQLite
    try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
    INSERT INTO alunos (nome, telefone, email, curso, nivel_ippi, observacoes, data_cadastro)
    VALUES (?, ?, ?, ?, ?, ?, ?)
""", (
    dados['nome'].strip(),
    dados['telefone'].strip(),
    dados['email'].strip().lower(),
    dados['curso'],
    dados.get('nivel_ippi', ''),
    dados.get('observacoes', '').strip(),
    data_cadastro
))
            conn.commit() 
            novo_id = cursor.lastrowid
            conn.close()
            return jsonify({'mensagem': 'Aluno cadastrado com sucesso!', 'id': novo_id}), 201
    except Exception as e:
        # Tratamento de erro especifico para e-mails duplicados (UNIQUE constraint)
        if 'UNIQUE constraint failed' in str(e):
            return jsonify({'erro': 'Este e-mail já está cadastrado.'}), 400
        return jsonify({'erro': str(e)}), 500

@app.route('/buscar_aluno/<int:aluno_id>', methods = ['GET'])
def buscar_aluno(aluno_id):
    """
   Busca um aluno pelo ID.
    ---
    tags:
      - Alunos
    parameters:
      - in: path
        name: aluno_id
        type: integer
        required: true
        description: ID do aluno
    responses:
      200:
        description: Aluno encontrado
      404:
        description: Aluno não encontrado
    """

    conn = get_connection()
    aluno = conn.execute("Select * FROM alunos WHERE id = ?", (aluno_id,)).fetchone()
    conn.close()

    # Retorno 404 caso o ID não exista no banco
    if aluno is None:
        return jsonify({"erro": "Aluno não encontrado."}), 404

    # Converte o objeto Row do SQLite em um dicionário para JSON
    return jsonify(dict(aluno)), 200

@app.route("/buscar_alunos", methods = ["GET"])
def buscar_alunos():
    """
   Retorna a lista de todos os alunos cadastrados.
    ---
    tags:
      - Alunos
    responses:
      200:
        description: Lista de alunos
    """
    conn = get_connection()
    alunos = conn.execute("SELECT * FROM  alunos ORDER BY data_cadastro DESC").fetchall()
    conn.close()
    
    return jsonify ({
        "total": len(alunos),
        "alunos": [dict(a) for a in alunos]
    }), 200
    

@app.route("/buscar_por_curso", methods = ["GET"])
def buscar_por_curso():
    """
   Filtra alunos por curso.
    ---
    tags:
      - Alunos
    parameters:
      - in: query
        name: curso
        type: string
        required: true
        description: Nome do curso
    responses:
      200:
        description: Lista de alunos do curso
      400:
        description: Curso inválido
    """
    curso = request.args.get("curso", "").strip()

    if not curso:
        return jsonify({"erro": "Curso inválido.", "cursos_validos": CURSOS_VALIDOS})
    
    conn = get_connection()
    alunos = conn.execute(
        "SELECT * FROM alunos WHERE curso = ? ORDER BY nome", (curso,)
    ).fetchall()
    conn.close()
    return jsonify({
        "curso": curso,
        "total": len(alunos),  
        "alunos": [dict(a) for a in alunos]
    }), 200

@app.route('/atualizar_aluno/<int:aluno_id>', methods=['PUT'])
def atualizar_aluno(aluno_id):
    """
    Atualiza os dados de um aluno.
    ---
    tags:
      - Alunos
    parameters:
      - in: path
        name: aluno_id
        type: integer
        required: true
        description: ID do aluno
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            nome:
              type: string
            telefone:
              type: string
            email:
              type: string
            curso:
              type: string
            nivel_ippi:
              type: string
            observacoes:
              type: string
    responses:
      200:
        description: Aluno atualizado com sucesso
      404:
        description: Aluno não encontrado
    """
    conn = get_connection()
    aluno = conn.execute('SELECT * FROM alunos WHERE id = ?', (aluno_id,)).fetchone()

    if aluno is None:
        conn.close()
        return jsonify({'erro': 'Aluno não encontrado.'}), 404

    aluno = dict(aluno)
    dados = request.get_json()

    # Logica de "Merge": Se o campo não for enviado no JSON, mantem o valor atual
    nome        = dados.get('nome',        aluno['nome']).strip()
    telefone    = dados.get('telefone',    aluno['telefone']).strip()
    email       = dados.get('email',       aluno['email']).strip().lower()
    curso       = dados.get('curso',       aluno['curso'])
    nivel_ippi  = dados.get('nivel_ippi',  aluno['nivel_ippi'])
    observacoes = dados.get('observacoes', aluno['observacoes'])

    # Validação da regra de negócio antes do Update
    if curso not in CURSOS_VALIDOS:
        conn.close()
        return jsonify({'erro': 'Curso inválido.'}), 400

    try:
        conn.execute('''
            UPDATE alunos
            SET nome=?, telefone=?, email=?, curso=?, nivel_ippi=?, observacoes=?
            WHERE id=?
        ''', (nome, telefone, email, curso, nivel_ippi, observacoes, aluno_id))
        conn.commit()
        conn.close()
        return jsonify({'mensagem': 'Aluno atualizado com sucesso!'}), 200
    except Exception as e:
        conn.close()
        if 'UNIQUE constraint failed' in str(e):
            return jsonify({'erro': 'Este e-mail já está em uso.'}), 400
        return jsonify({'erro': 'Erro interno.'}), 500
@app.route('/deletar_aluno/<int:aluno_id>', methods=['DELETE'])
def deletar_aluno(aluno_id):
    """
    Remove um aluno pelo ID.
    ---
    tags:
      - Alunos
    parameters:
      - in: path
        name: aluno_id
        type: integer
        required: true
        description: ID do aluno
    responses:
      200:
        description: Aluno removido com sucesso
      404:
        description: Aluno não encontrado
    """
    conn = get_connection()
    aluno = conn.execute('SELECT * FROM alunos WHERE id = ?', (aluno_id,)).fetchone()

    if aluno is None:
        conn.close()
        return jsonify({'erro': 'Aluno não encontrado.'}), 404

    conn.execute('DELETE FROM alunos WHERE id = ?', (aluno_id,))
    conn.commit()
    conn.close()

    return jsonify({'mensagem': 'Aluno removido com sucesso!'}), 200

# Inicialização do Servidor
if __name__ == "__main__":
    # Garnte que as tabelas existam antes da API começar a aceitar requisições
    init_db()
    print("Banco de dados inicializado")
    print("Documentação disposnivel em http://localhost:5000/apidocs")

    # Roda em modo debug para facilitar o desesnvolvimento (hot-reload)
    app.run(debug = True, port = 5000)

