from flask import Flask, request, jsonify
from flask_cors import CORS
from flasgger import Swagger
from database import init_db, get_connection
from datetime import datetime
import sqlite3

# Inicialização da aplicação Flask
app = Flask(__name__)

# Configuração do CORS
CORS(app, resources={r"/*": {"origins": "*"}})

@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
    return response

# Configuração do Flasgger / Swagger UI
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
    "specs_route": "/apidocs"
}

template = {
    "swagger": "2.0",
    "info": {
        "title": "Flutuar API - Escola de Parapente",
        "description": "API RESTful para gestão de alunos/pilotos e consulta de condições climáticas.",
        "version": "1.0.0"
    },
    "paths": {
        "/buscar_alunos": {
            "get": {
                "tags": ["Alunos"],
                "summary": "Listar todos os alunos cadastrados",
                "responses": {
                    "200": {"description": "Lista de alunos retornada com sucesso"}
                }
            }
        },
        "/cadastrar_aluno": {
            "post": {
                "tags": ["Alunos"],
                "summary": "Cadastrar um novo aluno",
                "parameters": [
                    {
                        "name": "body",
                        "in": "body",
                        "required": True,
                        "schema": {
                            "type": "object",
                            "required": ["nome", "telefone", "email", "curso"],
                            "properties": {
                                "nome": {"type": "string", "example": "Carlos Silva"},
                                "telefone": {"type": "string", "example": "(21) 99999-8888"},
                                "email": {"type": "string", "example": "carlos@email.com"},
                                "curso": {"type": "string", "example": "Iniciante"},
                                "nivel_ippi": {"type": "string", "example": "2"},
                                "observacoes": {"type": "string", "example": "Piloto em formação"}
                            }
                        }
                    }
                ],
                "responses": {
                    "201": {"description": "Aluno cadastrado com sucesso"},
                    "400": {"description": "Dados inválidos ou e-mail já cadastrado"}
                }
            }
        },
        "/buscar_aluno/{aluno_id}": {
            "get": {
                "tags": ["Alunos"],
                "summary": "Buscar aluno por ID",
                "parameters": [
                    {
                        "name": "aluno_id",
                        "in": "path",
                        "required": True,
                        "type": "integer",
                        "description": "ID do aluno"
                    }
                ],
                "responses": {
                    "200": {"description": "Dados do aluno"},
                    "404": {"description": "Aluno não encontrado"}
                }
            }
        },
        "/atualizar_aluno/{aluno_id}": {
            "put": {
                "tags": ["Alunos"],
                "summary": "Atualizar dados do aluno",
                "parameters": [
                    {
                        "name": "aluno_id",
                        "in": "path",
                        "required": True,
                        "type": "integer"
                    },
                    {
                        "name": "body",
                        "in": "body",
                        "required": True,
                        "schema": {
                            "type": "object",
                            "properties": {
                                "nome": {"type": "string", "example": "Carlos Silva"},
                                "telefone": {"type": "string", "example": "(21) 99999-8888"},
                                "email": {"type": "string", "example": "carlos@email.com"},
                                "curso": {"type": "string", "example": "Iniciante", "description": "Valores aceitos: Iniciante, Cross, Voo Duplo"},
                                "nivel_ippi": {"type": "string", "example": "2"},
                                "observacoes": {"type": "string", "example": "Piloto em formação"}
                            }
                        }
                    }
                ],
                "responses": {
                    "200": {"description": "Aluno atualizado com sucesso"},
                    "400": {"description": "Curso inválido ou dados incorretos"},
                    "404": {"description": "Aluno não encontrado"}
                }
            }
        },
        "/deletar_aluno/{aluno_id}": {
            "delete": {
                "tags": ["Alunos"],
                "summary": "Remover aluno",
                "parameters": [
                    {
                        "name": "aluno_id",
                        "in": "path",
                        "required": True,
                        "type": "integer"
                    }
                ],
                "responses": {
                    "200": {"description": "Aluno removido com sucesso"}
                }
            }
        },
        "/clima": {
            "get": {
                "tags": ["Clima"],
                "summary": "Consultar condições climáticas para voo",
                "parameters": [
                    {
                        "name": "cidade",
                        "in": "query",
                        "type": "string",
                        "required": False,
                        "default": "Rio de Janeiro",
                        "description": "Nome da cidade"
                    }
                ],
                "responses": {
                    "200": {"description": "Retorna temperatura, velocidade, direção do vento e condição de voo"}
                }
            }
        }
    }
}

Swagger(app, config=swagger_config, template=template)

CURSOS_VALIDOS = ["Iniciante", "Cross", "Voo Duplo"]
NIVEIS_IPPI = ["1", "2", "3", "4"]

@app.route("/cadastrar_aluno", methods=["POST", "OPTIONS"])
@app.route("/aluno", methods=["POST", "OPTIONS"])
def cadastrar_aluno():
    if request.method == "OPTIONS":
        return jsonify({}), 200

    dados = request.get_json() or {}

    for campo in ["nome", "telefone", "email", "curso"]:
        if not dados.get(campo, "").strip():
            return jsonify({"erro": f"Campo obrigatório ausente: {campo}"}), 400

    if dados["curso"] not in CURSOS_VALIDOS:
        return jsonify({"erro": "Curso invalido.", "cursos_validos": CURSOS_VALIDOS}), 400

    if dados.get("nivel_ippi") and dados["nivel_ippi"] not in NIVEIS_IPPI:
        return jsonify({"erro": "Nível IPPI inválido.", "niveis_validos": NIVEIS_IPPI}), 400

    data_cadastro = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    conn = None
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
        return jsonify({'mensagem': 'Aluno cadastrado com sucesso!', 'id': novo_id}), 201
    except sqlite3.IntegrityError:
        return jsonify({'erro': 'Este e-mail já está cadastrado.'}), 400
    except Exception as e:
        return jsonify({'erro': str(e)}), 500
    finally:
        if conn:
            conn.close()

@app.route('/buscar_aluno/<int:aluno_id>', methods=['GET'])
@app.route('/aluno/<int:aluno_id>', methods=['GET'])
def buscar_aluno(aluno_id):
    conn = None
    try:
        conn = get_connection()
        aluno = conn.execute("SELECT * FROM alunos WHERE id = ?", (aluno_id,)).fetchone()

        if aluno is None:
            return jsonify({"erro": "Aluno não encontrado."}), 404

        return jsonify(dict(aluno)), 200
    except Exception as e:
        return jsonify({'erro': str(e)}), 500
    finally:
        if conn:
            conn.close()

@app.route("/buscar_alunos", methods=["GET"])
@app.route("/alunos", methods=["GET"])
def buscar_alunos():
    conn = None
    try:
        conn = get_connection()
        alunos = conn.execute("SELECT * FROM alunos ORDER BY data_cadastro DESC").fetchall()
        return jsonify({
            "total": len(alunos),
            "alunos": [dict(a) for a in alunos]
        }), 200
    except Exception as e:
        return jsonify({'erro': str(e)}), 500
    finally:
        if conn:
            conn.close()

@app.route("/buscar_por_curso", methods=["GET"])
def buscar_por_curso():
    curso = request.args.get("curso", "").strip()

    if not curso:
        return jsonify({"erro": "Curso inválido.", "cursos_validos": CURSOS_VALIDOS}), 400

    conn = None
    try:
        conn = get_connection()
        alunos = conn.execute(
            "SELECT * FROM alunos WHERE curso = ? ORDER BY nome", (curso,)
        ).fetchall()
        return jsonify({
            "curso": curso,
            "total": len(alunos),
            "alunos": [dict(a) for a in alunos]
        }), 200
    except Exception as e:
        return jsonify({'erro': str(e)}), 500
    finally:
        if conn:
            conn.close()

@app.route('/atualizar_aluno/<int:aluno_id>', methods=['PUT'])
def atualizar_aluno(aluno_id):
    conn = None
    try:
        conn = get_connection()
        aluno = conn.execute('SELECT * FROM alunos WHERE id = ?', (aluno_id,)).fetchone()

        if aluno is None:
            return jsonify({'erro': 'Aluno não encontrado.'}), 404

        aluno = dict(aluno)
        dados = request.get_json() or {}

        nome        = dados.get('nome',        aluno['nome']).strip()
        telefone    = dados.get('telefone',    aluno['telefone']).strip()
        email       = dados.get('email',       aluno['email']).strip().lower()
        curso       = dados.get('curso',       aluno['curso'])
        nivel_ippi  = dados.get('nivel_ippi',  aluno['nivel_ippi'])
        observacoes = dados.get('observacoes', aluno['observacoes'])

        if curso not in CURSOS_VALIDOS:
            return jsonify({'erro': 'Curso inválido.'}), 400

        conn.execute('''
            UPDATE alunos
            SET nome=?, telefone=?, email=?, curso=?, nivel_ippi=?, observacoes=?
            WHERE id=?
        ''', (nome, telefone, email, curso, nivel_ippi, observacoes, aluno_id))
        conn.commit()
        return jsonify({'mensagem': 'Aluno atualizado com sucesso!'}), 200
    except Exception as e:
        if 'UNIQUE constraint failed' in str(e):
            return jsonify({'erro': 'Este e-mail já está em uso.'}), 400
        return jsonify({'erro': 'Erro interno.'}), 500
    finally:
        if conn:
            conn.close()

@app.route('/deletar_aluno/<int:aluno_id>', methods=['DELETE'])
def deletar_aluno(aluno_id):
    conn = None
    try:
        conn = get_connection()
        aluno = conn.execute('SELECT * FROM alunos WHERE id = ?', (aluno_id,)).fetchone()

        if aluno is None:
            return jsonify({'erro': 'Aluno não encontrado.'}), 404

        conn.execute('DELETE FROM alunos WHERE id = ?', (aluno_id,))
        conn.commit()
        return jsonify({'mensagem': 'Aluno removido com sucesso!'}), 200
    except Exception as e:
        return jsonify({'erro': str(e)}), 500
    finally:
        if conn:
            conn.close()

@app.route('/clima', methods=['GET'])
def consultar_clima():
    import requests
    cidade = request.args.get('cidade', 'Rio de Janeiro').strip()
    url = f"https://wttr.in/{cidade}?format=j1"
    
    try:
        resposta = requests.get(url, timeout=5)
        if resposta.status_code == 200:
            dados = resposta.json()
            condicao_atual = dados["current_condition"][0]
            
            temp_c = condicao_atual["temp_C"]
            vento_kmh = float(condicao_atual["windspeedKmph"])
            direcao_vento = condicao_atual.get("winddir16Point", "N/A")
            descricao = condicao_atual["lang_pt"][0]["value"] if "lang_pt" in condicao_atual else condicao_atual["weatherDesc"][0]["value"]
            
            condicao_voo = "Favorável para Voo" if vento_kmh < 25 else "Atenção: Vento Forte"
            
            return jsonify({
                "cidade": cidade,
                "temperatura_c": temp_c,
                "descricao": descricao,
                "vento_kmh": vento_kmh,
                "direcao_vento": direcao_vento,
                "condicao_voo": condicao_voo
            }), 200
        else:
            return jsonify({"erro": "Não foi possível obter dados da cidade solicitada."}), 400
            
    except Exception as e:
        return jsonify({"erro": f"Erro na comunicação com a API de clima: {str(e)}"}), 500

if __name__ == '__main__':
    init_db()
    print("Banco de dados inicializado")
    print("Documentação disponível em http://localhost:5000/apidocs")
    app.run(host='0.0.0.0', port=5000, debug=True)